from __future__ import annotations

from dataclasses import dataclass

from .histogram import HistogramBuilder
from .scoring import Scorer
from .solver import Solver
from .views import HideView, SolveView
from .words import Dictionary, Word


@dataclass
class SolveController:
    """Controller for the Solve entry point"""

    dictionary: Dictionary
    scorer: Scorer
    histogram_builder: HistogramBuilder
    solver: Solver
    view: SolveView

    def solve(self, first_guess: Word | None) -> bool:
        """Solves a game given an optional opening guess.

        Args:
            first_guess (Word | None): The opening guess.

        Returns:
          bool: True is the solve was successful.
        """
        all_words, available_answers = self.dictionary.words
        best_guess = first_guess or self.solver.seed(all_words.word_length)

        while True:
            (observed_score, best_guess) = self.view.get_user_score(best_guess)
            if self.scorer.is_perfect_score(observed_score):
                self.view.report_success()
                return True

            histogram = self.histogram_builder.get_solns_by_score(available_answers, best_guess)
            if observed_score not in histogram:
                self.view.report_no_solution()
                return False

            available_answers = histogram[observed_score]
            best_guess = self.solver.get_best_guess(all_words, available_answers).word
            self.view.report_best_guess(best_guess)


@dataclass
class HideController:
    """Controller for the Hide entry point"""

    dictionary: Dictionary
    scorer: Scorer
    histogram_builder: HistogramBuilder
    view: HideView

    def hide(self, first_guess: Word | None) -> None:
        """Hides a solution for as long as possible.

        Args:
            first_guess (Word | None): An optional opening guess
        """
        available_answers = self.dictionary.common_words
        guess = first_guess or self.view.get_user_guess()

        MAX_ITERS = 100
        for i in range(1, MAX_ITERS):
            histogram = self.histogram_builder.get_solns_by_score(available_answers, guess)

            def rank_score(score: int) -> int:
                solutions = histogram[score]
                return 0 if guess in solutions else len(solutions)

            highest_score = max(histogram, key=rank_score)
            available_answers = histogram[highest_score]
            self.view.update(i, guess, highest_score, available_answers)

            if self.scorer.is_perfect_score(highest_score):
                self.view.report_success()
                break

            guess = self.view.get_user_guess()
