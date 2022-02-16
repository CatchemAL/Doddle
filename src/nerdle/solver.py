from __future__ import annotations

import abc
from dataclasses import dataclass
from ftplib import all_errors
from math import isclose
from typing import Dict, Iterator, List, Protocol, Set

import numpy as np
from numba import njit

from nerdle.words import WordSeries

from .scoring import Scorer


class Guess(Protocol):
    word: str
    is_common_word: bool


class HistogramBuilder:
    pass


class PrecalculatedScores:
    def __init__(self, potential_solns: WordSeries, all_words: WordSeries, scorer: Scorer) -> None:
        self.all_words = all_words
        self.potential_solns = potential_solns
        self.scorer = scorer

        rows, cols = all_words.index.max() + 1, potential_solns.index.max() + 1
        self.is_calculated = np.zeros(cols, dtype=bool)
        self.score_matrix = np.full((rows, cols), -1, dtype=int)

    def precompute(self, potential_solns: WordSeries | None = None) -> None:

        solns = potential_solns or self.potential_solns
        if np.all(self.is_calculated[solns.index]):
            return

        f = np.vectorize(self.scorer.score_word)
        row_words = self.all_words.words[:, np.newaxis]
        col_words = solns.words[np.newaxis, :]
        self.score_matrix[:, solns.index] = f(row_words, col_words)
        self.is_calculated[solns.index] = True


class Solver(abc.ABC):
    def __init__(self, scorer: Scorer) -> None:
        self.scorer = scorer
        self.is_initialized = False
        self.storage = None

    @abc.abstractmethod
    def get_best_guess(self, potential_solutions: Set[str], all_words: Set[str]) -> Guess:
        pass

    def initialize(self, potential_solutions: WordSeries, all_words: WordSeries) -> None:
        if self.is_initialized:
            return

        self.storage = PrecalculatedScores(potential_solutions, all_words, self.scorer)
        self.is_initialized = True

    def all_guesses(
        self, potential_solutions: WordSeries, all_words: WordSeries
    ) -> Iterator[Guess]:

        # First we precompute the score against all possible words
        self.initialize(potential_solutions, all_words)  # this is a hack
        self.storage.precompute(potential_solutions)  # this is not

        indices = all_words.find_index(potential_solutions.words)

        if len(potential_solutions) > 2:
            words = all_words
            is_common = np.zeros(len(all_words), dtype=bool)
            is_common[indices] = True
            scores = self.storage.score_matrix[:, potential_solutions.index]
        else:
            words = all_words[indices]
            is_common = np.ones(len(words), dtype=bool)
            scores = self.storage.score_matrix[words.index, :][:, potential_solutions.index]

        histogram = np.zeros(3**self.scorer.size, dtype=int)
        for i, word in enumerate(words):
            populate_histogram(scores, i, histogram)
            num_buckets = np.count_nonzero(histogram)
            largest_bucket = histogram.max()
            yield MinimaxGuess(word, is_common[i], num_buckets, largest_bucket)

    @abc.abstractmethod
    def create_guess(word: str, potential_solutions: Set[str], histogram: Dict[int, int]) -> Guess:
        pass

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


@njit
def populate_histogram(matrix: np.ndarray, row: int, hist: np.ndarray) -> None:
    hist[:] = 0
    for j in range(matrix.shape[1]):
        idx = matrix[row, j]
        hist[idx] += 1


class MinimaxSolver(Solver):
    def get_best_guess(self, potential_solutions: Set[str], all_words: Set[str]) -> MinimaxGuess:
        guesses = self.all_guesses(potential_solutions, all_words)
        return min(guesses)

    def create_guess(
        self, word: str, potential_solutions: WordSeries, histogram: Dict[int, int]
    ) -> Guess:

        number_of_buckets = len(histogram)
        size_of_largest_bucket = max(histogram.values())
        is_common_word = word in potential_solutions.words

        return MinimaxGuess(word, is_common_word, number_of_buckets, size_of_largest_bucket)


class DeepMinimaxSolver(MinimaxSolver):
    def __init__(self, inner_solver: MinimaxSolver) -> None:
        super().__init__(inner_solver.scorer)
        self.solver = inner_solver

    def get_best_guess(self, potential_solutions: Set[str], all_words: Set[str]) -> MinimaxGuess:

        N_GUESSES = 20
        N_BRANCHES = 5

        guesses = self.all_guesses(potential_solutions, all_words)
        best_guesses = sorted(guesses)[:N_GUESSES]

        nested_worst_best_guess_by_guess: Dict[str, Guess] = {}

        for guess in best_guesses:
            solns_by_score = self.scorer.get_solutions_by_score(potential_solutions, guess.word)
            worst_outcomes = sorted(solns_by_score, key=lambda s: -len(solns_by_score[s]))
            nested_best_guesses: List[Guess] = []
            for worst_outcome in worst_outcomes[:N_BRANCHES]:
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
class MinimaxGuess:

    word: str
    is_common_word: bool
    number_of_buckets: int
    size_of_largest_bucket: int

    def improves_upon(self, other: MinimaxGuess) -> bool:

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
        flag = "Common" if self.is_common_word else "Uncommon"
        return (
            f"Word={self.word} ({flag}), Largest bucket={self.size_of_largest_bucket}, "
            + f"Num. buckets={self.number_of_buckets}"
        )

    def __lt__(self, other: MinimaxGuess):
        return self.improves_upon(other)

    def __gt__(self, other: MinimaxGuess):
        return other.improves_upon(self)


class EntropySolver(Solver):
    def get_best_guess(self, potential_solutions: Set[str], all_words: Set[str]) -> EntropyGuess:
        guesses = self.all_guesses(potential_solutions, all_words)
        return min(guesses)

    def create_guess(
        self, word: str, potential_solutions: Set[str], histogram: Dict[int, int]
    ) -> EntropyGuess:

        probabilites = np.array(list(histogram.values()), dtype=np.float64)
        probabilites /= len(potential_solutions)
        entropy = -probabilites.dot(np.log2(probabilites))
        is_common_word = word in potential_solutions

        return EntropyGuess(word, is_common_word, entropy)


class DeepEntropySolver(EntropySolver):
    def __init__(self, inner_solver: EntropySolver) -> None:
        super().__init__(inner_solver.scorer)
        self.solver = inner_solver

    def get_best_guess(self, potential_solutions: Set[str], all_words: Set[str]) -> EntropyGuess:

        N_GUESSES = 10

        guesses = self.all_guesses(potential_solutions, all_words)
        best_guesses = sorted(guesses)[:N_GUESSES]
        deep_guesses: List[EntropyGuess] = []

        for guess in best_guesses:
            solns_by_outcome = self.scorer.get_solutions_by_score(potential_solutions, guess.word)

            if guess.is_common_word and all(len(s) == 1 for s in solns_by_outcome.values()):
                return guess

            avg_entropy_reduction = 0
            for nested_potential_solns in solns_by_outcome.values():
                probability = len(nested_potential_solns) / len(potential_solutions)
                nested_best_guess = self.solver.get_best_guess(nested_potential_solns, all_words)
                entropy_reduction = nested_best_guess.entropy * probability
                avg_entropy_reduction += entropy_reduction
            deep_guesses.append(guess + avg_entropy_reduction)

        deep_best_guess = min(deep_guesses)
        return deep_best_guess


@dataclass
class EntropyGuess:

    word: str
    is_common_word: bool
    entropy: float

    def improves_upon(self, other: EntropyGuess) -> bool:

        if not isclose(self.entropy, other.entropy, abs_tol=1e-9):
            return self.entropy > other.entropy
        if self.is_common_word and not other.is_common_word:
            return True
        if other.is_common_word and not self.is_common_word:
            return False
        return self.word < other.word

    def __str__(self) -> str:
        return self.word

    def __repr__(self) -> str:
        flag = "Common" if self.is_common_word else "Uncommon"
        return f"Word={self.word} ({flag}), Entropy={self.entropy}"

    def __lt__(self, other: EntropyGuess):
        return self.improves_upon(other)

    def __gt__(self, other: EntropyGuess):
        return other.improves_upon(self)

    def __add__(self, entropy: float) -> EntropyGuess:
        return EntropyGuess(self.word, self.is_common_word, self.entropy + entropy)
