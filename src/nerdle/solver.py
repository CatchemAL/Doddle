from __future__ import annotations

import abc
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Set

from .scoring import Scorer


class Solver:
    def __init__(self, scorer: Scorer) -> None:
        self.scorer = scorer

    def prettify(self, solution: str, guess: str) -> None:
        score = self.scorer.score_word(solution, guess)
        size = len(solution)
        padded_score = f"{score}".zfill(size)
        message = f"{solution}, {guess}, {padded_score}"
        print(message)

    @abc.abstractmethod
    def get_best_guess(self, possible_solutions: Set[str], available_guesses: Set[str]) -> str:
        pass

    def get_possible_solutions_by_score(
        self, possible_solutions: Set[str], guess: str
    ) -> Dict[int, Set[str]]:
        possible_solutions_by_score = defaultdict(set)
        for solution in possible_solutions:
            score = self.scorer.score_word(solution, guess)
            possible_solutions_by_score[score].add(solution)

        return possible_solutions_by_score

    @staticmethod
    def seed(size: int) -> str:

        seed_by_size = {
            4: "OLEA",
            5: "RAISE",
            6: "TAILER",
            7: "TENAILS",
            8: "CENTRALS",
            9: "SECRETION",
        }

        return seed_by_size[size]


class MinimaxSolver(Solver):
    def get_best_guess(self, possible_solutions: Set[str], available_guesses: Set[str]) -> str:

        best_guess_to_date = Guess("N/A", 1_000_000, 1_000_000)

        for guess in available_guesses:
            possible_solutions_by_score = self.get_possible_solutions_by_score(
                possible_solutions, guess
            )
            new_guess = Guess.create(guess, possible_solutions_by_score)

            if new_guess.improves_upon(best_guess_to_date, possible_solutions):
                best_guess_to_date = new_guess

        return best_guess_to_date.word


class DeeperMinimaxSolver(Solver):
    def get_best_guess(self, possible_solutions: Set[str], available_guesses: Set[str]) -> str:

        best_guess_to_date = Guess("N/A", 1_000_000, 1_000_000)

        for guess in available_guesses:
            possible_solutions_by_score = self.get_possible_solutions_by_score(
                possible_solutions, guess
            )

            # TODO look at possible solutions for subsequent round of guesses

            new_guess = Guess.create(guess, possible_solutions_by_score)

            if new_guess.improves_upon(best_guess_to_date, possible_solutions):
                best_guess_to_date = new_guess

        return best_guess_to_date.word


@dataclass
class Guess:

    word: str
    size_of_largest_bucket: int
    number_of_buckets: int

    def improves_upon(self, other: Guess, common_words: Set[str]) -> bool:

        if self.size_of_largest_bucket != other.size_of_largest_bucket:
            return self.size_of_largest_bucket < other.size_of_largest_bucket

        if self.word in common_words:
            if other.word not in common_words:
                return True
        else:
            if other.word in common_words:
                return False

        if self.number_of_buckets != other.number_of_buckets:
            return self.number_of_buckets > other.number_of_buckets

        return self.word < other.word

    @staticmethod
    def create(guess: str, possible_solutions_by_score: Dict[int, Set[str]]) -> Guess:

        groups = possible_solutions_by_score.values()
        number_of_buckets = len(groups)
        size_of_largest_bucket = max(len(group) for group in groups)
        return Guess(guess, size_of_largest_bucket, number_of_buckets)
