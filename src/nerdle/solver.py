from __future__ import annotations

import abc
from dataclasses import dataclass
from math import isclose
from typing import Iterator

import numpy as np

from .histogram import Guess, HistogramBuilder
from .words import Word, WordSeries


class Solver(abc.ABC):
    def __init__(self, histogram_builder: HistogramBuilder) -> None:
        self.hist_builder = histogram_builder

    @abc.abstractmethod
    def get_best_guess(self, potential_solns: WordSeries, all_words: WordSeries) -> Guess:
        pass

    # TODO NO - THIS IS A FUNCTION OF THE SOLVER
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

        return Word(seed_by_size[size])


class MinimaxSolver(Solver):

    # todo: potentially an implict vs explicit implementation
    def get_best_guess(self, potential_solns: WordSeries, all_words: WordSeries) -> MinimaxGuess:
        return min(self.all_guesses(potential_solns, all_words))

    def all_guesses(self, potential_solns: WordSeries, all_words: WordSeries) -> Iterator[MinimaxGuess]:

        if len(potential_solns) <= 2:
            yield MinimaxGuess(potential_solns.words[0], True, 1, 1)
        else:
            yield from self.hist_builder.stream(potential_solns, all_words, self._create_guess)

    @staticmethod
    def _create_guess(word: Word, is_common_word: bool, histogram: np.ndarray) -> Guess:
        num_buckets = np.count_nonzero(histogram)
        size_of_largest_bucket = histogram.max()
        return MinimaxGuess(word, is_common_word, num_buckets, size_of_largest_bucket)


class DeepMinimaxSolver(MinimaxSolver):
    def __init__(self, histogram_builder: HistogramBuilder, inner_solver: MinimaxSolver) -> None:
        super().__init__(histogram_builder)
        self.inner = inner_solver

    def get_best_guess(self, potential_solns: WordSeries, all_words: WordSeries) -> MinimaxGuess:

        N_GUESSES = 20
        N_BRANCHES = 5

        guesses = self.all_guesses(potential_solns, all_words)
        best_guesses = sorted(guesses)[:N_GUESSES]

        deep_worst_best_guess_by_guess: dict[str, MinimaxGuess] = {}

        for guess in best_guesses:
            solns_by_score = self.hist_builder.get_solns_by_score(potential_solns, guess.word)
            worst_outcomes = sorted(solns_by_score, key=lambda s: -len(solns_by_score[s]))
            nested_best_guesses: list[Guess] = []
            for worst_outcome in worst_outcomes[:N_BRANCHES]:
                nested_potential_solns = solns_by_score[worst_outcome]
                nested_best_guess = self.inner.get_best_guess(nested_potential_solns, all_words)
                nested_best_guesses.append(nested_best_guess)
            worst_best_guess = max(nested_best_guesses)
            deep_worst_best_guess_by_guess[guess.word] = worst_best_guess

        best_guess_str = min(deep_worst_best_guess_by_guess, key=deep_worst_best_guess_by_guess.get)
        best_guess = next(guess for guess in best_guesses if guess.word == best_guess_str)
        return best_guess # TODO bug. Guess needs to convey depth of lower levels! Will affect 3+


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
    def get_best_guess(self, potential_solns: WordSeries, all_words: WordSeries) -> EntropyGuess:
        guesses = self.all_guesses(potential_solns, all_words)
        return min(guesses)

    def create_guess(
        self, word: str, potential_solns: WordSeries, histogram: dict[int, int]
    ) -> EntropyGuess:

        probabilites = np.array(list(histogram.values()), dtype=np.float64)
        probabilites /= len(potential_solns)
        entropy = -probabilites.dot(np.log2(probabilites))
        is_common_word = word in potential_solns

        return EntropyGuess(word, is_common_word, entropy)


class DeepEntropySolver(EntropySolver):
    def __init__(self, inner_solver: EntropySolver) -> None:
        super().__init__(inner_solver.scorer)
        self.solver = inner_solver

    def get_best_guess(self, potential_solns: WordSeries, all_words: WordSeries) -> EntropyGuess:

        N_GUESSES = 10

        guesses = self.all_guesses(potential_solns, all_words)
        best_guesses = sorted(guesses)[:N_GUESSES]
        deep_guesses: list[EntropyGuess] = []

        for guess in best_guesses:
            solns_by_outcome = self.scorer.get_solutions_by_score(potential_solns, guess.word)

            if guess.is_common_word and all(len(s) == 1 for s in solns_by_outcome.values()):
                return guess

            avg_entropy_reduction = 0
            for nested_potential_solns in solns_by_outcome.values():
                probability = len(nested_potential_solns) / len(potential_solns)
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
