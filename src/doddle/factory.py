from __future__ import annotations

from sqlite3 import NotSupportedError  # TODO
from typing import Sequence

from .engine import Benchmarker, Engine, SimulBenchmarker, SimulEngine
from .enums import SolverType
from .histogram import HistogramBuilder
from .scoring import Scorer
from .simul_solver import MinimaxSimulSolver, SimulSolver
from .solver import DeepEntropySolver, DeepMinimaxSolver, EntropySolver, MinimaxSolver, Solver
from .views import BenchmarkView, NullRunView, RunView
from .words import Dictionary, Word, load_dictionary


def create_simul_engine(
    size: int,
    *,
    solver_type: SolverType = SolverType.MINIMAX,
    depth: int = 1,
    extras: Sequence[Word] | None = None,
    lazy_eval: bool = True,
    reporter: RunView | None = None,
) -> SimulEngine:

    dictionary, scorer, histogram_builder, _, simul_solver = create_models(
        size, solver_type=solver_type, depth=depth, extras=extras, lazy_eval=lazy_eval
    )

    reporter = reporter or RunView()
    return SimulEngine(dictionary, scorer, histogram_builder, simul_solver, reporter)


def create_engine(
    size: int,
    *,
    solver_type: SolverType = SolverType.MINIMAX,
    depth: int = 1,
    extras: Sequence[Word] | None = None,
    lazy_eval: bool = True,
    reporter: RunView | None = None,
) -> Engine:

    dictionary, scorer, histogram_builder, solver, _ = create_models(
        size, solver_type=solver_type, depth=depth, extras=extras, lazy_eval=lazy_eval
    )

    reporter = reporter or RunView()
    return Engine(dictionary, scorer, histogram_builder, solver, reporter)


def create_benchmarker(
    size: int,
    *,
    solver_type: SolverType = SolverType.MINIMAX,
    depth: int = 1,
    extras: Sequence[Word] | None = None,
) -> Benchmarker:
    engine = create_engine(
        size,
        solver_type=solver_type,
        depth=depth,
        extras=extras,
        lazy_eval=False,
        reporter=NullRunView(),
    )

    reporter = BenchmarkView()
    return Benchmarker(engine, reporter)


def create_simul_benchmarker(
    size: int,
    *,
    solver_type: SolverType = SolverType.MINIMAX,
    depth: int = 1,
    extras: Sequence[Word] | None = None,
) -> SimulBenchmarker:
    simul_engine = create_simul_engine(
        size,
        solver_type=solver_type,
        depth=depth,
        extras=extras,
        lazy_eval=False,
        reporter=NullRunView(),
    )

    reporter = BenchmarkView()
    return SimulBenchmarker(simul_engine, reporter)


def create_models(
    size: int,
    *,
    solver_type: SolverType = SolverType.MINIMAX,
    depth: int = 1,
    extras: Sequence[Word] | None = None,
    lazy_eval: bool = True,
) -> tuple[Dictionary, Scorer, HistogramBuilder, Solver, SimulSolver]:

    dictionary = load_dictionary(size, extras=extras)
    all_words, potential_solns = dictionary.words

    scorer = Scorer(size)
    histogram_builder = HistogramBuilder(scorer, all_words, potential_solns, lazy_eval)

    if solver_type == SolverType.MINIMAX:
        minimax_solver = MinimaxSolver(histogram_builder)
        for _ in range(1, depth):
            minimax_solver = DeepMinimaxSolver(histogram_builder, minimax_solver)
        solver: Solver = minimax_solver

    elif solver_type == SolverType.ENTROPY:
        entropy_solver = EntropySolver(histogram_builder)
        for _ in range(1, depth):
            entropy_solver = DeepEntropySolver(histogram_builder, entropy_solver)
        solver = entropy_solver
    else:
        raise NotSupportedError(f"Solver type {solver_type} not recognised.")

    simul_solver: SimulSolver = MinimaxSimulSolver(histogram_builder)

    return dictionary, scorer, histogram_builder, solver, simul_solver
