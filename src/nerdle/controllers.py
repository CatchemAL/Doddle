from dataclasses import dataclass

import numpy as np

from .histogram import HistogramBuilder
from .scoring import Scorer
from .solver import Solver
from .views import HideView, SolveView
from .words import Dictionary, Word


@dataclass
class SolveController:

    dictionary: Dictionary
    scorer: Scorer
    histogram_builder: HistogramBuilder
    solver: Solver
    view: SolveView

    def solve(self, first_guess: Word | None) -> None:

        all_words, available_answers = self.dictionary.words
        best_guess = first_guess or self.solver.seed(all_words.word_length)

        while True:
            (observed_score, best_guess) = self.view.get_user_score(best_guess)
            if self.scorer.is_perfect_score(observed_score):
                self.view.report_success()
                break

            histogram = self.histogram_builder.get_solns_by_score(available_answers, best_guess)
            available_answers = histogram.get(observed_score, None)

            if not available_answers:
                self.view.report_no_solution()
                break

            best_guess = self.solver.get_best_guess(all_words, available_answers).word
            self.view.report_best_guess(best_guess)


@dataclass
class HideController:

    dictionary: Dictionary
    scorer: Scorer
    histogram_builder: HistogramBuilder
    view: HideView

    def hide(self, first_guess: Word | None) -> None:

        available_answers = self.dictionary.common_words
        guess = first_guess or self.view.get_user_guess()

        for i in range(100):

            histogram = self.histogram_builder.get_solns_by_score(available_answers, guess)

            def rank_score(score: int) -> int:
                solutions = histogram[score]
                return 0 if guess in solutions else len(solutions)

            highest_score = max(histogram, key=rank_score)
            available_answers = histogram[highest_score]
            ternary_score = np.base_repr(highest_score, base=3)  # TODO busines log. TF callback?
            self.view.update(i, guess, ternary_score, available_answers)

            if self.scorer.is_perfect_score(highest_score):
                self.view.report_success()
                break

            guess = self.view.get_user_guess()
