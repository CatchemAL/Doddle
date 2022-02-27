from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Iterator

import colorama
from colorama import Fore

from .words import Word

if TYPE_CHECKING:
    import pandas as pd

colorama.init()


@dataclass
class ScoreboardRow:
    n: int
    soln: Word
    guess: Word
    score: str
    num_left: int

    def __repr__(self) -> str:
        a = f"n={self.n}, soln={self.soln}, guess={self.guess}, "
        b = f"score={self.score}, num_left={self.num_left}"
        return a + b

    def to_dict(self, use_emojis: bool = True) -> dict[str, Any]:

        score = self.score

        if use_emojis:
            score = score.replace("0", "⬜")
            score = score.replace("1", "🟨")
            score = score.replace("2", "🟩")

        return {
            "n": self.n,
            "Soln": str(self.soln),
            "Guess": str(self.guess),
            "Score": score,
            "Poss": self.num_left,
        }


class Scoreboard:
    def __init__(self) -> None:
        self.rows: list[ScoreboardRow] = []

    def add_row(
        self, n: int, soln: Word | None, guess: Word, score: str, num_left: int
    ) -> ScoreboardRow:

        answer = soln if soln else Word("?" * len(guess))
        row = ScoreboardRow(n, answer, guess, score, num_left)
        self.rows.append(row)
        return row

    def __len__(self):
        return len(self.rows)

    def __iter__(self) -> Iterator[ScoreboardRow]:
        return iter(self.rows)

    def __next__(self) -> ScoreboardRow:
        return next(self.rows)  # type: ignore

    def df(self, use_emojis: bool = True) -> pd.DataFrame:
        try:
            import pandas as pd
        except ImportError:
            message = "Unable to create a DataFrame because pandas is not installed. "
            message += "Pandas is an optional dependency of doddle. To use this feature, "
            message += "install doddle via 'pip install doddle[df]'"
            raise ImportError(message)

        records = [row.to_dict(use_emojis) for row in self]
        df = pd.DataFrame.from_records(records)
        return df.set_index("n")


class ScoreboardPrinter:
    def __init__(self, size: int) -> None:
        self.size = size

    def print(self, scoreboard: Scoreboard) -> None:
        string_repr = self.build_string(scoreboard)
        print(string_repr)

    def print_last_round(self, scoreboard: Scoreboard) -> None:

        if len(scoreboard) == 0:
            return

        if scoreboard.rows[-1].n == 1:
            header = self.build_header()
            print(header)
        elif len([row.n for row in scoreboard.rows if row.n == 1]) > 1:
            divider = self.build_divider()
            print(divider)

        last_round = scoreboard.rows[-1].n
        last_rows = [row for row in scoreboard.rows if row.n == last_round]
        for row in last_rows:
            row_str_repr = self.build_row(row.n, row.soln, row.guess, row.score, row.num_left)
            print(row_str_repr)

    def build_string(self, scoreboard: Scoreboard) -> str:

        scoreboard_str_repr: list[str] = []
        header = self.build_header()
        scoreboard_str_repr.append(header)

        for row in scoreboard:
            row_str_repr = self.build_row(row.n, row.soln, row.guess, row.score, row.num_left)
            scoreboard_str_repr.append(row_str_repr)

        return "\n".join(scoreboard_str_repr)

    def build_header(self) -> str:
        repetitions = 0 if self.size <= 5 else (self.size - 5)
        spacing = " " * repetitions
        header = f"\n| # | Soln.{spacing} | Guess{spacing} | Score{spacing} | Poss.{spacing} |\n"
        header += self.build_divider()
        return header

    def build_divider(self) -> str:
        repetitions = 0 if self.size <= 5 else (self.size - 5)
        dashes = "-" * repetitions
        return f"|---|-------{dashes}|-------{dashes}|-------{dashes}|-------{dashes}|"

    def build_row(self, n: int, soln: Word, guess: Word, score: str, num_left: int) -> str:

        n2 = str(n).rjust(2, " ")

        padding = " " * max(0, 5 - self.size)
        num_left_str = " " if guess == soln else f"{num_left}"
        padded_num_left = num_left_str.rjust(max(5, self.size), " ")

        pretty_soln = soln + padding
        pretty_guess = self._color_code(guess, score) + padding
        pretty_score = self._color_code(score, score) + padding

        return f"|{n2} | {pretty_soln} | {pretty_guess} | {pretty_score} | {padded_num_left} |"

    @staticmethod
    def _color_code(word: Word | str, score: str) -> str:

        prev_digit = "0"
        pretty_chars = []
        for (char, digit) in zip(word, score):
            if digit == prev_digit:
                pretty_chars.append(char)
            elif digit == "2":
                pretty_chars.append(Fore.GREEN + char)
            elif digit == "1":
                pretty_chars.append(Fore.YELLOW + char)
            else:
                pretty_chars.append(Fore.RESET + char)
            prev_digit = digit

        if prev_digit != "0":
            pretty_chars.append(Fore.RESET)

        return "".join(pretty_chars)


class Keyboard:
    def __init__(self) -> None:

        self.digit_by_char: defaultdict[str, int] = defaultdict(lambda: -1)

    def update(self, word: Word | str, score: str) -> None:

        for (char, digit_str) in zip(word, score):
            digit = int(digit_str)
            current_digit = self.digit_by_char[char]
            self.digit_by_char[char] = max(current_digit, digit)


class KeyboardPrinter:
    def print(self, keyboard: Keyboard) -> None:
        string_repr = self.build_string(keyboard)
        print(string_repr)

    @staticmethod
    def build_string(keyboard: Keyboard) -> str:
        UNSET = -1
        BOARD = """
    Q  W  E  R  T  Y  U  I  O  P
     A  S  D  F  G  H  J  K  L
      Z  X  C  V  B  N  M
      """

        prev_digit = UNSET
        pretty_chars = []
        for char in BOARD:
            if not char.isalpha():
                pretty_chars.append(char)
                continue

            digit = keyboard.digit_by_char[char]

            # TODO duplicate logic with other class
            if digit == prev_digit:
                pretty_chars.append(char)
            elif digit == 2:
                pretty_chars.append(Fore.GREEN + char)
            elif digit == 1:
                pretty_chars.append(Fore.YELLOW + char)
            elif digit == 0:
                pretty_chars.append(Fore.LIGHTBLACK_EX + char)
            else:
                pretty_chars.append(Fore.RESET + char)
            prev_digit = digit

        if prev_digit != UNSET:
            pretty_chars.append(Fore.RESET)

        return "".join(pretty_chars)
