from __future__ import annotations

import abc
from collections import defaultdict
from dataclasses import dataclass
from functools import cmp_to_key
from typing import DefaultDict, Dict, Iterator, Set

import numpy as np

from .scoring import Scorer


class Solver:
    def __init__(self, scorer: Scorer) -> None:
        self.scorer = scorer

    @abc.abstractmethod
    def get_best_guess(self, potential_solutions: Set[str], all_words: Set[str]) -> str:
        pass

    def get_solutions_by_score(self, potential_solns: Set[str], guess: str) -> Dict[int, Set[str]]:
        potential_solns_by_score = defaultdict(set)
        for soln in potential_solns:
            score = self.scorer.score_word(soln, guess)
            potential_solns_by_score[score].add(soln)

        return potential_solns_by_score

    def get_histogram(self, potential_solns: Set[str], guess: str) -> DefaultDict[int, int]:
        histogram = defaultdict(int)
        for soln in potential_solns:
            score = self.scorer.score_word(soln, guess)
            histogram[score] += 1

        return histogram

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
    def get_best_guess(self, potential_solutions: Set[str], all_words: Set[str]) -> Guess:
        guesses = self.all_guesses(potential_solutions, all_words)
        return min(guesses)

    def all_guesses(self, potential_solutions: Set[str], all_words: Set[str]) -> Iterator[Guess]:
        for word in all_words:
            histogram = self.get_histogram(potential_solutions, word)
            guess = Guess.create(word, potential_solutions, histogram)
            yield guess


class DeepMinimaxSolver(MinimaxSolver):
    def __init__(self, inner_solver: Solver) -> None:
        super().__init__(inner_solver.scorer)
        self.solver = inner_solver

    def get_best_guess(self, potential_solutions: Set[str], all_words: Set[str]) -> Guess:

        N_BRANCH = 5

        guesses = self.all_guesses(potential_solutions, all_words)
        best_guesses = sorted(guesses)[:N_BRANCH]

        nested_worst_best_guess_by_guess = {}

        for guess in best_guesses:
            solns_by_score = self.get_solutions_by_score(potential_solutions, guess.word)
            worst_outcomes = sorted(solns_by_score, key=lambda s: -len(solns_by_score[s]))
            nested_best_guesses = []
            for worst_outcome in worst_outcomes[:N_BRANCH]:
                nested_potential_solns = solns_by_score[worst_outcome]
                nested_best_guess = self.solver.get_best_guess(nested_potential_solns, all_words)
                nested_best_guesses.append(nested_best_guess)
            worst_best_guess = max(nested_best_guesses)
            nested_worst_best_guess_by_guess[guess.word] = worst_best_guess

        kvps = nested_worst_best_guess_by_guess.items()
        best_nested_worst_best_guess = min(nested_worst_best_guess_by_guess.values())
        best_guess_str = next(key for key, value in kvps if value == best_nested_worst_best_guess)
        best_guess = next(guess for guess in best_guesses if guess.word == best_guess_str)
        return best_guess


@dataclass
class Guess:

    word: str
    size_of_largest_bucket: int
    number_of_buckets: int
    entropy: float
    is_common_word: bool

    def improves_upon(self, other: Guess) -> bool:

        if self.size_of_largest_bucket != other.size_of_largest_bucket:
            return self.size_of_largest_bucket < other.size_of_largest_bucket

        if self.is_common_word and not other.is_common_word:
            return True
        if other.is_common_word and not self.is_common_word:
            return False

        if self.number_of_buckets != other.number_of_buckets:
            return self.number_of_buckets > other.number_of_buckets

        return self.word < other.word

    def __str__(self) -> str:
        return self.word

    def __repr__(self) -> str:
        return (
            f"Word={self.word}, Largest bucket={self.size_of_largest_bucket}, "
            + f"Num. buckets={self.number_of_buckets}, Entropy={self.entropy}"
        )

    def __lt__(self, other: Guess):
        return self.improves_upon(other)

    def __gt__(self, other: Guess):
        return other.improves_upon(self)

    @staticmethod
    def create(word: str, potential_solutions: Set[str], histogram: Dict[int, int]) -> Guess:

        buckets = np.array(list(histogram.values()))
        probabilites = buckets / buckets.sum()
        entropy = -probabilites.dot(np.log2(probabilites))

        number_of_buckets = len(histogram)
        size_of_largest_bucket = max(buckets)
        is_common_word = word in potential_solutions

        return Guess(word, size_of_largest_bucket, number_of_buckets, entropy, is_common_word)
