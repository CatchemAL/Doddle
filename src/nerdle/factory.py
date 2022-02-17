from typing import Tuple

from nerdle.histogram import HistogramBuilder

from .scoring import Scorer
from .solver import DeepEntropySolver, DeepMinimaxSolver, EntropySolver, MinimaxSolver, Solver
from .words import WordSeries


def create_models(
    available_answers: WordSeries, all_words: WordSeries, depth: int
) -> Tuple[Scorer, HistogramBuilder, Solver]:
    scorer = Scorer(all_words.word_length)
    histogram_builder = HistogramBuilder(scorer, available_answers, all_words)

    solver = MinimaxSolver(histogram_builder)
    for _ in range(1, depth):
        solver = DeepMinimaxSolver(histogram_builder, solver)

    if False:
        solver = EntropySolver(histogram_builder)
        for _ in range(1, depth):
            solver = DeepEntropySolver(histogram_builder, solver)

    return scorer, histogram_builder, solver
