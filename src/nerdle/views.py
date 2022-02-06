import re
from typing import Set, Tuple

from .view_models import Keyboard, KeyboardPrinter, Scoreboard, ScoreboardPrinter


class HideView:
    def __init__(self, size: int) -> None:
        self.scoreboard = Scoreboard()
        self.keyboard = Keyboard()
        self.size = size

    def update(self, word: str, score: int, available_answers: Set[str]) -> None:

        sb_printer = ScoreboardPrinter(self.size)
        kb_printer = KeyboardPrinter()

        num_left = len(available_answers)
        soln = word if num_left == 1 and word in available_answers else None
        self.scoreboard.add_row(soln, word, score, num_left)
        sb_printer.print(self.scoreboard)

        self.keyboard.update(word, score)
        kb_printer.print(self.keyboard)

    def report_success(self) -> None:
        message = "You win! 🙌 👏 🙌"
        print(message)

    def get_user_guess(self) -> str:
        guess = ""
        while len(guess) != self.size or not guess.isalpha():
            guess = input("Please enter your next guess:\n").upper()

        return guess


class RunView:
    def __init__(self, size: int) -> None:
        self.size = size
        self.scoreboard = Scoreboard()

    def report_score(
        self, solution: str, guess: str, score: int, available_answers: Set[str]
    ) -> None:
        self.scoreboard.add_row(solution, guess, score, len(available_answers))

        sb_printer = ScoreboardPrinter(self.size)
        sb_printer.print_next(self.scoreboard)


class SolveView:

    score_expr = re.compile(r"[0-2]+$")
    word_expr = re.compile(r"^([A-Z]+)=([0-2]+)$")

    def __init__(self, size: int) -> None:
        self.size = size

    def report_success(self) -> None:
        message = "\nGreat success! ✨ 🔮 ✨"
        print(message)

    def report_no_solution(self) -> None:
        message = "\nOh no! Nerdle does not know of any words that match those scores! 😭 😭 😭"
        print(message)

    def report_best_guess(self, best_guess: str) -> None:
        message = f"\nThe best guess is {best_guess}"
        print(message)

    def get_user_score(self, guess: str) -> Tuple[int, str]:

        is_valid = False

        while not is_valid:
            user_response = input(f"Enter score for {guess}:\n")
            sanitized_response = user_response.upper().replace(" ", "")
            (observed_score, guess, is_valid) = self._parse_response(guess, sanitized_response)

        return (observed_score, guess)

    def _parse_response(self, guess: str, response: str) -> Tuple[int, str, bool]:

        if len(response) == self.size and self.score_expr.match(response):
            observed_score = int(response)
            return (observed_score, guess, True)

        m = self.word_expr.match(response)

        if len(response) == (2 * self.size + 1) and response[self.size] == "=" and m:
            (user_guess, score) = m.groups()
            return (int(score), user_guess, True)

        return (-1, guess, False)
