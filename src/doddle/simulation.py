from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import partial

import numpy as np

from .exceptions import FailedToFindASolutionError
from .histogram import HistogramBuilder
from .quordle import QuordleGame, QuordleSolver
from .scoring import Scorer
from .solver import Solver
from .views import BenchmarkView, RunView
from .words import Dictionary, Word


@dataclass
class MultiSimulator:

    dictionary: Dictionary
    scorer: Scorer
    histogram_builder: HistogramBuilder
    solver: QuordleSolver
    reporter: RunView

    def run_multi(self, solutions: list[Word], first_guess: Word | None) -> int:  # TODO return more
        all_words, common_words = self.dictionary.words
        best_guess = first_guess or self.solver.seed(all_words.word_length)
        games = QuordleGame.games(common_words, solutions)

        MAX_ITERS = 15
        for i in range(MAX_ITERS):
            for game in games:
                if game.is_solved:
                    continue
                available_answers = game.available_answers
                histogram = self.histogram_builder.get_solns_by_score(available_answers, best_guess)
                score = self.scorer.score_word(game.soln, best_guess)
                updated_answers = histogram[score]
                self.reporter.report_score(i, game.soln, best_guess, score, updated_answers)
                game.available_answers = updated_answers
                game.is_solved = best_guess == game.soln  # TODO set number of moves

            if all((game.is_solved for game in games)):
                return i + 1  # TODO return games I suppose

            best_guess = self.solver.get_best_guess(all_words, games).word

        raise FailedToFindASolutionError(f"Failed to converge after {MAX_ITERS} iterations.")


@dataclass
class Simulator:

    dictionary: Dictionary
    scorer: Scorer
    histogram_builder: HistogramBuilder
    solver: Solver
    reporter: RunView

    def run(self, solution: Word, first_guess: Word | None) -> int:  # TODO return more
        all_words, available_answers = self.dictionary.words
        best_guess = first_guess or self.solver.seed(all_words.word_length)

        MAX_ITERS = 15
        for i in range(MAX_ITERS):
            histogram = self.histogram_builder.get_solns_by_score(available_answers, best_guess)
            score = self.scorer.score_word(solution, best_guess)
            available_answers = histogram[score]
            self.reporter.report_score(i, solution, best_guess, score, available_answers)

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
