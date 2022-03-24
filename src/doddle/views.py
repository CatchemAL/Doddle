from __future__ import annotations

import re
from collections import defaultdict

from .boards import Keyboard, KeyboardPrinter, Scoreboard, ScoreboardPrinter
from .game import DoddleGame
from .scoring import from_ternary, to_ternary
from .words import Word, WordSeries


class InputMixin:
    def get_input(self, prompt: str) -> str:
        return input(prompt)  # pragma: no cover


class RunReporter:
    """Realtime reporter to display progress of a DoddleGame during a solve."""

    def display(self, game: DoddleGame) -> None:
        """Displays an update on the solve progress.

        Args:
            game (DoddleGame): A DoddleGame.
        """
        sb_printer = ScoreboardPrinter(game.word_length)
        sb_printer.print_last_round(game.scoreboard)


class NullRunReporter(RunReporter):
    """Null implementation of a RunReporter"""

    def display(self, _: DoddleGame) -> None:
        """Does nothing"""
        pass


class SolveView(InputMixin):

    score_expr = re.compile(r"[0-2]+$")
    word_expr = re.compile(r"^([A-Z]+)=([0-2]+)$")

    def __init__(self, size: int) -> None:
        self.size = size

    def report_success(self) -> None:
        message = "\nGreat success! ✨ 🔮 ✨"
        print(message)

    def report_no_solution(self) -> None:
        message = "\nOh no! Doddle does not know of any words that match those scores! 😭 😭 😭"
        print(message)

    def report_best_guess(self, best_guess: Word) -> None:
        message = f"\nThe best guess is {best_guess}"
        print(message)

    def get_user_score(self, guess: Word) -> tuple[int, Word]:

        is_valid = False

        while not is_valid:
            user_response = self.get_input(f"Enter score for {guess}:\n")
            sanitized_response = user_response.upper().replace(" ", "")
            (observed_score, guess, is_valid) = self._parse_response(guess, sanitized_response)

        return (observed_score, guess)

    def _parse_response(self, guess: Word, response: str) -> tuple[int, Word, bool]:

        if len(response) == self.size and self.score_expr.match(response):
            observed_score = from_ternary(response)
            return (observed_score, guess, True)

        m = self.word_expr.match(response)

        if len(response) == (2 * self.size + 1) and response[self.size] == "=" and m:
            (user_guess, score) = m.groups()
            return (from_ternary(score), Word(user_guess), True)

        return (-1, guess, False)


class HideView(InputMixin):
    def __init__(self, size: int) -> None:
        self.scoreboard = Scoreboard()
        self.keyboard = Keyboard()
        self.size = size

    def update(self, n: int, word: Word, score: int, available_answers: WordSeries) -> None:

        ternary_score = to_ternary(score, self.size)

        sb_printer = ScoreboardPrinter(self.size)
        kb_printer = KeyboardPrinter()

        num_left = len(available_answers)
        soln = word if num_left == 1 and word in available_answers else None
        self.scoreboard.add_row(n, soln, word, ternary_score, num_left)
        sb_printer.print(self.scoreboard)

        self.keyboard.update(word, ternary_score)
        kb_printer.print(self.keyboard)

    def report_success(self) -> None:
        message = "You win! 🙌 👏 🙌"
        print(message)

    def get_user_guess(self) -> Word:
        guess = ""
        while len(guess) != self.size or not guess.isalpha():
            guess = self.get_input("Please enter your guess:\n").upper()

        return Word(guess)


class BenchmarkReporter:
    def display(self, histogram: defaultdict[int, int]) -> None:
        print("| # | Count |")
        print("|---|-------|")

        for (num, count) in sorted(histogram.items()):
            padded_num_left = f"{count:,}".rjust(5, " ")
            print(f"| {num} | {padded_num_left} |")
