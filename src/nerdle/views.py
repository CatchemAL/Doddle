import abc
import re
from typing import DefaultDict, Set, Tuple

from .view_models import Keyboard, KeyboardPrinter, Scoreboard, ScoreboardPrinter
from .words import Word, WordSeries


class AbstractRunView:
    @abc.abstractmethod
    def report_score(self, solution: str, guess: str, score: int, available_answers: Set[str]) -> None:
        pass


class RunView(AbstractRunView):
    def __init__(self, size: int) -> None:
        self.size = size
        self.scoreboard = Scoreboard()

    def report_score(
        self, solution: Word, guess: Word, score: int, available_answers: WordSeries
    ) -> None:

        self.scoreboard.add_row(str(solution), str(guess), score, len(available_answers))

        sb_printer = ScoreboardPrinter(self.size)
        sb_printer.print_next(self.scoreboard)


class SilentRunView(AbstractRunView):
    """View that doesn't show anything."""

    def report_score(
        self, solution: Word, guess: Word, score: int, available_answers: WordSeries
    ) -> None:
        pass


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

    def get_user_score(self, guess: Word) -> Tuple[int, Word]:

        is_valid = False

        while not is_valid:
            user_response = input(f"Enter score for {guess}:\n")
            sanitized_response = user_response.upper().replace(" ", "")
            (observed_score, guess, is_valid) = self._parse_response(guess, sanitized_response)

        return (observed_score, guess)

    def _parse_response(self, guess: Word, response: str) -> Tuple[int, Word, bool]:

        if len(response) == self.size and self.score_expr.match(response):
            observed_score = self._ternary_to_dec(response)
            return (observed_score, guess, True)

        m = self.word_expr.match(response)

        if len(response) == (2 * self.size + 1) and response[self.size] == "=" and m:
            (user_guess, score) = m.groups()
            return (self._ternary_to_dec(score), Word(user_guess), True)

        return (-1, guess, False)

    @staticmethod
    def _ternary_to_dec(ternary: str) -> int:
        # TODO move to utils class
        value = 0
        digits = [int(digit) for digit in reversed(list(ternary))]
        for i, num in enumerate(digits):
            value += num * (3**i)
        return value


class HideView:
    def __init__(self, size: int) -> None:
        self.scoreboard = Scoreboard()
        self.keyboard = Keyboard()
        self.size = size

    def update(self, word: Word, score: int, available_answers: Set[str]) -> None:

        sb_printer = ScoreboardPrinter(self.size)
        kb_printer = KeyboardPrinter()

        num_left = len(available_answers)
        soln = str(word) if num_left == 1 and word in available_answers else None
        self.scoreboard.add_row(soln, str(word), score, num_left)
        sb_printer.print(self.scoreboard)

        self.keyboard.update(str(word), score)
        kb_printer.print(self.keyboard)

    def report_success(self) -> None:
        message = "You win! 🙌 👏 🙌"
        print(message)

    def get_user_guess(self) -> Word:
        guess = ""
        while len(guess) != self.size or not guess.isalpha():
            guess = input("Please enter your guess:\n").upper()

        return Word(guess)


class BenchmarkView:
    def display(self, histogram: DefaultDict[int, int]) -> None:
        print("| # | Count |")
        print("|---|-------|")

        for (num, count) in sorted(histogram.items()):
            padded_num_left = f"{count:,}".rjust(5, " ")
            print(f"| {num} | {padded_num_left} |")
