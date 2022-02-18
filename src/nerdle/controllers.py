import numpy as np

from .factory import create_models
from .views import HideView, SolveView
from .words import Word, load_dictionary


class SolveController:
    def __init__(self, loader, view: SolveView) -> None:
        self.loader = loader
        self.view = view

    def solve(self, first_guess: Word | None) -> None:

        dictionary = load_dictionary(size, guess=first_guess)
        all_words, available_answers = dictionary.words

        depth = 1  # TODO depth
        scorer, histogram_builder, solver = create_models(available_answers, all_words, depth)
        best_guess = first_guess or solver.seed(all_words.word_length)

        while True:
            (observed_score, best_guess) = self.view.get_user_score(best_guess)
            if scorer.is_perfect_score(observed_score):
                self.view.report_success()
                break

            histogram = histogram_builder.get_solns_by_score(available_answers, best_guess)
            available_answers = histogram.get(observed_score, None)

            if not available_answers:
                self.view.report_no_solution()
                break

            best_guess = solver.get_best_guess(available_answers, all_words).word
            self.view.report_best_guess(best_guess)


class HideController:
    def __init__(self, loader, view: HideView) -> None:
        self.loader = loader
        self.view = view

    def hide(self, first_guess: Word) -> None:

        all_words, available_answers = self.loader(guess=first_guess)

        depth = 1  # TODO depth
        scorer, histogram_builder, _ = create_models(available_answers, all_words, depth)
        guess = first_guess or self.view.get_user_guess()

        while True:

            histogram = histogram_builder.get_solns_by_score(available_answers, guess)

            def rank_score(score: int) -> int:
                solutions = histogram[score]
                return 0 if guess in solutions else len(solutions)

            highest_score = max(histogram, key=rank_score)
            available_answers = histogram[highest_score]
            ternary_score = np.base_repr(highest_score, base=3)  # TODO busines log. TF callback?
            self.view.update(guess, ternary_score, available_answers)

            if scorer.is_perfect_score(highest_score):
                self.view.report_success()
                break

            guess = self.view.get_user_guess()
