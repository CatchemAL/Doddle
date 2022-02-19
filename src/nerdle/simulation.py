from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import partial

import numpy as np

from .exceptions import FailedToFindASolutionError
from .histogram import HistogramBuilder
from .scoring import Scorer
from .solver import Solver
from .views import BenchmarkView, RunView
from .words import Dictionary, Word


@dataclass
class Simulator:

    dictionary: Dictionary
    scorer: Scorer
    histogram_builder: HistogramBuilder
    solver: Solver  # TODO depth
    reporter: RunView

    def run(self, solution: Word, first_guess: Word | None) -> int:  # TODO return more
        all_words, available_answers = self.dictionary.words
        best_guess = first_guess or self.solver.seed(all_words.word_length)

        MAX_ITERS = 15
        for i in range(MAX_ITERS):
            histogram = self.histogram_builder.get_solns_by_score(available_answers, best_guess)
            observed_score = self.scorer.score_word(solution, best_guess)
            available_answers = histogram[observed_score]
            ternary_score = np.base_repr(observed_score, base=3)  # TODO inappropriate bus. logic
            self.reporter.report_score(solution, best_guess, ternary_score, available_answers)

            if best_guess == solution:
                return i + 1

            best_guess = self.solver.get_best_guess(all_words, available_answers).word

        raise FailedToFindASolutionError(f"Failed to converge after {MAX_ITERS} iterations.")


class Benchmarker:
    def __init__(self, simulator: Simulator, reporter: BenchmarkView) -> None:
        self.simulator = simulator
        self.reporter = reporter

    def run_benchmark(self, first_guess: Word | None) -> None:

        dictionary = self.simulator.dictionary
        f = partial(self.simulator.run, first_guess=first_guess)

        with ProcessPoolExecutor(max_workers=8) as executor:
            n_guess = executor.map(f, dictionary.common_words)

        histogram: defaultdict[int, int] = defaultdict(int)
        for n in n_guess:
            histogram[n] += 1

        self.reporter.display(histogram)
