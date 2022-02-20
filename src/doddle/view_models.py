from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterator

import colorama
from colorama import Fore

from .words import Word

colorama.init()


@dataclass
class ScoreboardRow:
    n: int
    soln: Word
    guess: Word
    score: int
    num_left: int

    def __repr__(self) -> str:
        return f"{self.n=}, {self.soln=}, {self.guess=}, {self.score=}, {self.num_left=}"


class Scoreboard:
    def __init__(self) -> None:
        self.rows: list[ScoreboardRow] = []

    def add_row(
        self, n: int, soln: Word | None, guess: Word, score: int, num_left: int
    ) -> ScoreboardRow:

        if not soln:
            size = len(guess)
            soln = "?" * size

        row = ScoreboardRow(n + 1, soln, guess, score, num_left)
        self.rows.append(row)
        return row

    def __len__(self):
        return len(self.rows)

    def __iter__(self) -> Iterator[ScoreboardRow]:
        return iter(self.rows)

    def __next__(self) -> ScoreboardRow:
        return next(self.rows)


class ScoreboardPrinter:
    def __init__(self, size: int) -> None:
        self.size = size

    def print(self, scoreboard: Scoreboard) -> None:
        string_repr = self.build_string(scoreboard)
        print(string_repr)

    def print_next(self, scoreboard: Scoreboard) -> None:

        if len(scoreboard) == 1:
            header = self.build_header()
            print(header)
        elif scoreboard.rows[-1].n > scoreboard.rows[-2].n:
            is_multi_game_mode = len([row.n for row in scoreboard.rows if row.n == 1]) > 1
            if is_multi_game_mode:
                divider = self.build_divider()
                print(divider)

        row = scoreboard.rows[-1]
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

    def build_row(self, n: int, soln: Word, guess: Word, score: int, num_left: int) -> str:

        n2 = str(n).rjust(2, " ")

        padding = " " * max(0, 5 - self.size)
        padded_score = f"{score}".zfill(self.size)
        num_left_str = " " if guess == soln else f"{num_left}"
        padded_num_left = num_left_str.rjust(max(5, self.size), " ")

        pretty_soln = soln + padding
        pretty_guess = self._color_code(guess, score) + padding
        pretty_score = self._color_code(padded_score, score) + padding

        return f"|{n2} | {pretty_soln} | {pretty_guess} | {pretty_score} | {padded_num_left} |"

    @staticmethod
    def _color_code(word: Word | str, score: int) -> str:

        size = len(word)
        padded_score = f"{score}".zfill(size)

        prev_digit = "0"
        pretty_chars = []
        for (char, digit) in zip(word, padded_score):
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
        self.digit_by_char = defaultdict(lambda: -1)

    def update(self, word: Word | str, score: int) -> None:

        size = len(word)
        padded_score = f"{score}".zfill(size)
        for (char, digit_str) in zip(word, padded_score):
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
