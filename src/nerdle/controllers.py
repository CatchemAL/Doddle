from functools import partial

import numpy as np

from .factory import create_models

from .benchmark import benchmark

from .views import AbstractRunView, BenchmarkView, HideView, SilentRunView, SolveView
from .words import Word, WordLoader


class RunController:
    def __init__(self, loader: WordLoader, view: AbstractRunView) -> None:
        self.loader = loader
        self.view = view

    def run(self, solution: Word, first_guess: Word | None) -> int:

        MAX_ITERS = 15

        all_words, available_answers = self.loader(soln=solution, guess=first_guess)

        depth = 1 # TODO depth
        scorer, histogram_builder, solver = create_models(available_answers, all_words, depth)
        best_guess = first_guess or solver.seed(all_words.word_length)

        for i in range(MAX_ITERS):
            histogram = histogram_builder.get_solns_by_score(available_answers, best_guess)
            observed_score = scorer.score_word(solution, best_guess)
            available_answers = histogram[observed_score]
            ternary_score = np.base_repr(observed_score, base=3)  # TODO busines log. TF callback?
            self.view.report_score(solution, best_guess, ternary_score, available_answers)

            if best_guess == solution:
                return i + 1

            best_guess = solver.get_best_guess(available_answers, all_words).word

        raise LookupError(f"Failed to converge after {MAX_ITERS} iterations.")  # TODO custom error


class SolveController:
    def __init__(self, loader: WordLoader, view: SolveView) -> None:
        self.loader = loader
        self.view = view

    def solve(self, first_guess: Word | None) -> None:

        all_words, available_answers = self.loader(guess=first_guess)

        depth = 1 # TODO depth
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
    def __init__(self, loader: WordLoader, view: HideView) -> None:
        self.loader = loader
        self.view = view

    def hide(self, first_guess: Word) -> None:

        all_words, available_answers = self.loader(guess=first_guess)

        depth = 1 # TODO depth
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


class BenchmarkController:
    def __init__(self, loader: WordLoader, view: BenchmarkView) -> None:
        self.loader = loader
        self.view = view

    def run(self, first_guess: Word) -> None:

        all_words, available_answers = self.loader(guess=first_guess)

        depth = 1 # TODO depth
        _, _, solver = create_models(available_answers, all_words, depth)
        best_guess = first_guess or solver.seed(all_words.word_length)

        controller = RunController(self.loader, self.solver, SilentRunView())
        f = partial(controller.run, best_guess=best_guess)

        histogram = benchmark(f, available_answers)

        self.view.display(histogram)
