import re
from collections import defaultdict

from .view_models import Keyboard, KeyboardPrinter, Scoreboard, ScoreboardPrinter
from .words import Word, WordSeries
from .scoring import to_ternary

class RunView:
    def __init__(self, size: int) -> None:
        self.size = size
        self.scoreboard = Scoreboard()

    def report_score(
        self, n: int, solution: Word, guess: Word, decimal_score: int, available_answers: WordSeries
    ) -> None:
        
        ternary_score = to_ternary(decimal_score, self.size)
        self.scoreboard.add_row(n, solution, guess, ternary_score, len(available_answers))

        sb_printer = ScoreboardPrinter(self.size)
        sb_printer.print_next(self.scoreboard)


class NullRunView(RunView):
    """View that doesn't show anything."""

    def report_score(
        self, n: int, solution: Word, guess: Word, score: int, available_answers: WordSeries
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
        message = "\nOh no! Doddle does not know of any words that match those scores! 😭 😭 😭"
        print(message)

    def report_best_guess(self, best_guess: Word) -> None:
        message = f"\nThe best guess is {best_guess}"
        print(message)

    def get_user_score(self, guess: Word) -> tuple[int, Word]:

        is_valid = False

        while not is_valid:
            user_response = input(f"Enter score for {guess}:\n")
            sanitized_response = user_response.upper().replace(" ", "")
            (observed_score, guess, is_valid) = self._parse_response(guess, sanitized_response)

        return (observed_score, guess)

    def _parse_response(self, guess: Word, response: str) -> tuple[int, Word, bool]:

        if len(response) == self.size and self.score_expr.match(response):
            observed_score = self._ternary_to_dec(response)
            return (observed_score, guess, True)

        m = self.word_expr.match(response)

        if len(response) == (2 * self.size + 1) and response[self.size] == "=" and m:
            (user_guess, score) = m.groups()
            return (self._ternary_to_dec(score), Word(user_guess), True)

        return (-1, guess, False)




class HideView:
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
            guess = input("Please enter your guess:\n").upper()

        return Word(guess)


class BenchmarkView:
    def display(self, histogram: defaultdict[int, int]) -> None:
        print("| # | Count |")
        print("|---|-------|")

        for (num, count) in sorted(histogram.items()):
            padded_num_left = f"{count:,}".rjust(5, " ")
            print(f"| {num} | {padded_num_left} |")
