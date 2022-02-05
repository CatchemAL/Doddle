import re
from typing import Tuple

from colorama import Fore


class SimulationView:
    def __init__(self, size: int) -> None:
        self.size = size
        self.count = 0

    def report_score(self, solution: str, guess: str, score: int):
        if self.count == 0:
            header = self._build_header()
            print(header)

        self.count += 1
        row = self._build_row(solution, guess, score)
        print(row)

    def _build_header(self) -> str:
        repetitions = 0 if self.size <= 5 else (self.size - 5)
        spacing = " " * repetitions
        dashes = "-" * repetitions
        header = f"\n| # | Soln.{spacing} | Guess{spacing} | Score{spacing} |\n"
        header += f"|---|-------{dashes}|-------{dashes}|-------{dashes}|"
        return header

    def _build_row(self, soln: str, guess: str, score: int) -> str:

        padding = "" if self.size >= 5 else " " * (5 - self.size)
        padded_score = f"{score}".zfill(self.size)

        pretty_soln = soln + padding
        pretty_guess = self._color_code(guess, score) + padding
        pretty_score = self._color_code(padded_score, score) + padding
        return f"| {self.count} | {pretty_soln} | {pretty_guess} | {pretty_score} |"

    @staticmethod
    def _color_code(word: str, score: int) -> str:

        size = len(word)
        padded_score = f"{score}".zfill(size)

        pretty_chars = []
        for (char, digit) in zip(word, padded_score):
            if digit == "2":
                pretty_chars.append(Fore.GREEN + char)
            elif digit == "1":
                pretty_chars.append(Fore.YELLOW + char)
            else:
                pretty_chars.append(Fore.RESET + char)
        else:
            pretty_chars.append(Fore.RESET)

        return "".join(pretty_chars)


class ConsoleView:

    score_expr = re.compile(r"[0-2]+$")
    word_expr = re.compile(r"^([A-Z]+)=([0-2]+)$")

    def __init__(self, size: int) -> None:
        self.size = size

    def get_user_score(self, guess: str) -> Tuple[int, str]:

        is_valid = False

        while not is_valid:
            user_response = input(f"Enter observed score for {guess}:\n")
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
