from __future__ import annotations

from typing import Sequence

from doddle.guess import Guess

from .benchmarking import Benchmarker, BenchmarkReporter, SimulBenchmarker
from .engine import Engine, SimulEngine
from .enums import SolverType
from .exceptions import SolverNotSupportedError
from .histogram import HistogramBuilder
from .scoring import Scorer
from .simul_solver import EntropySimulSolver, MinimaxSimulSolver, SimulSolver
from .solver import DeepEntropySolver, DeepMinimaxSolver, EntropySolver, MinimaxSolver, Solver
from .views import NullRunReporter, RunReporter
from .words import Dictionary, Word, load_dictionary


def create_simul_engine(
    size: int,
    *,
    solver_type: SolverType = SolverType.MINIMAX,
    depth: int = 1,
    extras: Sequence[Word] | None = None,
    lazy_eval: bool = True,
    reporter: RunReporter | None = None,
) -> SimulEngine:

    dictionary, scorer, histogram_builder, _, simul_solver = create_models(
        size, solver_type=solver_type, depth=depth, extras=extras, lazy_eval=lazy_eval
    )

    reporter = reporter or RunReporter()
    return SimulEngine(dictionary, scorer, histogram_builder, simul_solver, reporter)


def create_engine(
    size: int,
    *,
    solver_type: SolverType = SolverType.MINIMAX,
    depth: int = 1,
    extras: Sequence[Word] | None = None,
    lazy_eval: bool = True,
    reporter: RunReporter | None = None,
) -> Engine:

    dictionary, scorer, histogram_builder, solver, _ = create_models(
        size, solver_type=solver_type, depth=depth, extras=extras, lazy_eval=lazy_eval
    )

    reporter = reporter or RunReporter()
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
        reporter=NullRunReporter(),
    )

    reporter = BenchmarkReporter()
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
        reporter=NullRunReporter(),
    )

    reporter = BenchmarkReporter()
    return SimulBenchmarker(simul_engine, reporter)


def create_models(
    size: int,
    *,
    solver_type: SolverType = SolverType.MINIMAX,
    depth: int = 1,
    extras: Sequence[Word] | None = None,
    lazy_eval: bool = True,
) -> tuple[Dictionary, Scorer, HistogramBuilder, Solver[Guess], SimulSolver[Guess, Guess]]:

    dictionary = load_dictionary(size, extras=extras)
    all_words, potential_solns = dictionary.words

    scorer = Scorer(size)
    histogram_builder = HistogramBuilder(scorer, all_words, potential_solns, lazy_eval)

    solver: Solver[Guess]
    simul_solver: SimulSolver[Guess, Guess]
    if solver_type == SolverType.MINIMAX:
        minimax_solver = MinimaxSolver(histogram_builder)
        for _ in range(1, depth):
            minimax_solver = DeepMinimaxSolver(histogram_builder, minimax_solver)
        solver = minimax_solver
        simul_solver = MinimaxSimulSolver(histogram_builder)

    elif solver_type == SolverType.ENTROPY:
        entropy_solver = EntropySolver(histogram_builder)
        for _ in range(1, depth):
            entropy_solver = DeepEntropySolver(histogram_builder, entropy_solver)
        solver = entropy_solver
        simul_solver = EntropySimulSolver(histogram_builder)

    else:
        raise SolverNotSupportedError(f"Solver type {solver_type} not recognised.")

    return dictionary, scorer, histogram_builder, solver, simul_solver
