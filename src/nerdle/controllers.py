from .solver import Solver
from .views import RunView
from .words import WordLoader


class RunController:
    def __init__(self, loader: WordLoader, solver: Solver, view: RunView) -> None:
        self.loader = loader
        self.solver = solver
        self.view = view

    def run(self, solution: str, best_guess: str) -> None:

        all_words = self.loader.all_words
        available_answers = self.loader.common_words

        while True:
            observed_score = self.solver.scorer.score_word(solution, best_guess)
            histogram = self.solver.get_possible_solutions_by_score(available_answers, best_guess)
            available_answers = histogram[observed_score]
            self.view.report_score(solution, best_guess, observed_score, available_answers)
            if best_guess == solution:
                break

            best_guess = self.solver.get_best_guess(available_answers, all_words)


class SolveController:
    def __init__(self, loader: WordLoader, solver: Solver, view: RunView) -> None:
        self.loader = loader
        self.solver = solver
        self.view = view

    def solve(self, best_guess: str) -> None:

        all_words = self.loader.all_words
        available_answers = self.loader.common_words

        while True:
            (observed_score, best_guess) = self.view.get_user_score(best_guess)
            if self.solver.scorer.is_perfect_score(observed_score):
                self.view.report_success()
                break

            histogram = self.solver.get_possible_solutions_by_score(available_answers, best_guess)
            available_answers = histogram[observed_score]
            best_guess = self.solver.get_best_guess(available_answers, all_words)
            self.view.report_best_guess(best_guess)


class HideController:
    def __init__(self, loader: WordLoader, solver: Solver, view: RunView) -> None:
        self.loader = loader
        self.solver = solver
        self.view = view

    def hide(self, best_guess: str) -> None:

        available_answers = self.loader.common_words

        while True:
            solutions_by_score = self.solver.get_possible_solutions_by_score(
                available_answers, best_guess
            )
            highest_score = max(solutions_by_score, key=lambda k: len(solutions_by_score[k]))

            # BUG! See issue #1 on GitHub
            available_answers = solutions_by_score[highest_score]
            self.view.update(best_guess, highest_score, available_answers)

            if self.solver.scorer.is_perfect_score(highest_score):
                self.view.report_success()
                break

            best_guess = self.view.get_user_guess()
