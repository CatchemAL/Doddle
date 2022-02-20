from sqlite3 import NotSupportedError
from typing import Sequence

from .histogram import HistogramBuilder
from .scoring import Scorer
from .simulation import Benchmarker, Simulator
from .solver import (
    DeepEntropySolver,
    DeepMinimaxSolver,
    EntropySolver,
    MinimaxSolver,
    Solver,
    SolverType,
)
from .views import BenchmarkView, NullRunView, RunView
from .words import Dictionary, Word, load_dictionary


def create_simulator(
    size: int,
    *,
    solver_type: SolverType = SolverType.MINIMAX,
    depth: int = 1,
    extras: Sequence[Word | None] | None = None,
    lazy_eval: bool = True,
    reporter: RunView | None = None,
) -> Simulator:

    dictionary, scorer, histogram_builder, solver = create_models(
        size, solver_type=solver_type, depth=depth, extras=extras, lazy_eval=lazy_eval
    )

    reporter = reporter or RunView(size)
    return Simulator(dictionary, scorer, histogram_builder, solver, reporter)


def create_benchmarker(
    size: int,
    *,
    solver_type: SolverType = SolverType.MINIMAX,
    depth: int = 1,
    extras: Sequence[Word | None] | None = None,
) -> Benchmarker:
    simulator = create_simulator(
        size,
        solver_type=solver_type,
        depth=depth,
        extras=extras,
        lazy_eval=False,
        reporter=NullRunView(size),
    )

    reporter = BenchmarkView()
    return Benchmarker(simulator, reporter)


def create_models(
    size: int,
    *,
    solver_type: SolverType = SolverType.MINIMAX,
    depth: int = 1,
    extras: Sequence[Word | None] | None = None,
    lazy_eval: bool = True,
) -> tuple[Dictionary, Scorer, HistogramBuilder, Solver]:

    dictionary = load_dictionary(size, extras=extras)
    all_words, potential_solns = dictionary.words

    scorer = Scorer(size)
    histogram_builder = HistogramBuilder(scorer, all_words, potential_solns, lazy_eval)

    if solver_type == SolverType.MINIMAX:
        solver = MinimaxSolver(histogram_builder)
        for _ in range(1, depth):
            solver = DeepMinimaxSolver(histogram_builder, solver)

    elif solver_type == SolverType.ENTROPY:
        solver = EntropySolver(histogram_builder)
        for _ in range(1, depth):
            solver = DeepEntropySolver(histogram_builder, solver)

    else:
        raise NotSupportedError(f"Solver type {solver_type} not recognised.")

    return dictionary, scorer, histogram_builder, solver
