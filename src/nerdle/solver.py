from __future__ import annotations

import abc
from dataclasses import dataclass
from enum import Enum
from math import isclose
from typing import Iterator

import numpy as np

from .histogram import Guess, HistogramBuilder
from .words import Word, WordSeries


class SolverType(Enum):
    MINIMAX = "MINIMAX"
    ENTROPY = "ENTROPY"

    @staticmethod
    def from_str(value: str) -> SolverType:
        if value.upper() == "MINIMAX":
            return SolverType.MINIMAX
        if value.upper() == "ENTROPY":
            return SolverType.ENTROPY
        supported_types = ", ".join(list(SolverType))
        message = (
            f"{value} not recognised as a valid solver type. "
            + f"Supported types are {supported_types}."
        )
        raise ValueError(message)


class Solver(abc.ABC):
    @abc.abstractmethod
    def get_best_guess(self, all_words: WordSeries, potential_solns: WordSeries) -> Guess:
        pass

    @property
    @abc.abstractmethod
    def all_seeds(self) -> list[Word]:
        pass

    def seed(self, size: int) -> Word:
        seed_by_size = {len(word): word for word in self.all_seeds}
        return seed_by_size[size]




@dataclass
class QuordleGuess:

    word: Word
    is_common_word: bool
    sum: int
    min: int
    max: int
    sum_pct: float
    min_pct: float
    max_pct: float
    pct_product: float


    def improves_upon(self, other: QuordleGuess) -> bool:



        if not isclose(self.pct_product, other.pct_product, abs_tol=1e-9):
            return self.pct_product < other.pct_product

        if self.sum != other.sum:
            return self.sum < other.sum

        if self.is_common_word and not other.is_common_word:
            return True
        if other.is_common_word and not self.is_common_word:
            return False

        if self.min != other.min:
            return self.min < other.min

        if self.max != other.max:
            return self.max < other.max

        return self.word < other.word

    def __str__(self) -> str:
        return str(self.word)

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



class QuordleSolver:
    def __init__(self, histogram_builder: HistogramBuilder) -> None:
        self.hist_builder = histogram_builder

    # todo: potentially an implict vs explicit implementation
    def get_best_guess(self, all_words: WordSeries, potential_solns_list: list(WordSeries)) -> MinimaxGuess:
        return min(self.all_guesses(all_words, potential_solns_list))

    def all_guesses(self, all_words: WordSeries, potential_solns_list: list(WordSeries)) -> Iterator[MinimaxGuess]:

        for potential_solns in potential_solns_list:
            if len(potential_solns) == 1:
                yield MinimaxGuess(potential_solns.words[0], True, 1, 1)
                return
    
        streams = []
        for potential_solns in potential_solns_list:
            stream = self.hist_builder.stream(all_words, potential_solns, self._create_guess)
            streams.append(stream)

        num_solutions = np.array([len(potential_solns) for potential_solns in potential_solns_list])
        for quad_guess in zip(*streams):
            guessed_word = quad_guess[0].word
            is_common_word = quad_guess[0].is_common_word
            largest_sizes = np.array([g.size_of_largest_bucket for g in quad_guess])
            largest_sizes_pct = largest_sizes / num_solutions
            sum = largest_sizes.sum()
            min = largest_sizes.min()
            max = largest_sizes.max()
            sum_pct = largest_sizes_pct.sum() # .dot(largest_sizes_pct)
            min_pct = largest_sizes_pct.min()
            max_pct = largest_sizes_pct.max()
            pct_product = largest_sizes_pct.prod()

            yield QuordleGuess(guessed_word, is_common_word, sum, min, max, sum_pct, min_pct, max_pct, pct_product)

    @property
    def all_seeds(self) -> list[Word]:
        seeds = {"OLEA", "RAISE", "TAILER", "TENAILS", "CENTRALS", "SECRETION"}
        return [Word(seed) for seed in seeds]

    @staticmethod
    def _create_guess(word: Word, is_common_word: bool, histogram: np.ndarray) -> MinimaxGuess:
        num_buckets = np.count_nonzero(histogram)
        size_of_largest_bucket = histogram.max()
        return MinimaxGuess(word, is_common_word, num_buckets, size_of_largest_bucket)



class MinimaxSolver(Solver):
    def __init__(self, histogram_builder: HistogramBuilder) -> None:
        self.hist_builder = histogram_builder

    # todo: potentially an implict vs explicit implementation
    def get_best_guess(self, all_words: WordSeries, potential_solns: WordSeries) -> MinimaxGuess:
        return min(self.all_guesses(all_words, potential_solns))

    def all_guesses(self, all_words: WordSeries, potential_solns: WordSeries) -> Iterator[MinimaxGuess]:

        if len(potential_solns) <= 2:
            yield MinimaxGuess(potential_solns.words[0], True, 1, 1)
        else:
            yield from self.hist_builder.stream(all_words, potential_solns, self._create_guess)

    @property
    def all_seeds(self) -> list[Word]:
        seeds = {"OLEA", "RAISE", "TAILER", "TENAILS", "CENTRALS", "SECRETION"}
        return [Word(seed) for seed in seeds]

    @staticmethod
    def _create_guess(word: Word, is_common_word: bool, histogram: np.ndarray) -> MinimaxGuess:
        num_buckets = np.count_nonzero(histogram)
        size_of_largest_bucket = histogram.max()
        return MinimaxGuess(word, is_common_word, num_buckets, size_of_largest_bucket)


class DeepMinimaxSolver(MinimaxSolver):
    def __init__(self, histogram_builder: HistogramBuilder, inner_solver: MinimaxSolver) -> None:
        super().__init__(histogram_builder)
        self.inner = inner_solver

    def get_best_guess(self, all_words: WordSeries, potential_solns: WordSeries) -> MinimaxGuess:

        N_GUESSES = 50
        N_BRANCHES = 10

        guesses = self.all_guesses(all_words, potential_solns)
        best_guesses = sorted(guesses)[:N_GUESSES]

        deep_worst_best_guess_by_guess: dict[Word, MinimaxGuess] = {}

        for guess in best_guesses:
            # TODO If perfect guess...
            solns_by_score = self.hist_builder.get_solns_by_score(potential_solns, guess.word)
            worst_outcomes = sorted(solns_by_score, key=lambda s: -len(solns_by_score[s]))
            nested_best_guesses: list[Guess] = []
            for worst_outcome in worst_outcomes[:N_BRANCHES]:
                nested_potential_solns = solns_by_score[worst_outcome]
                nested_best_guess = self.inner.get_best_guess(all_words, nested_potential_solns)
                nested_best_guesses.append(nested_best_guess)
            worst_best_guess = max(nested_best_guesses)
            deep_worst_best_guess_by_guess[guess.word] = worst_best_guess

        best_guess_str = min(deep_worst_best_guess_by_guess, key=deep_worst_best_guess_by_guess.get)
        best_guess = next(guess for guess in best_guesses if guess.word == best_guess_str)
        return best_guess  # TODO bug. Guess needs to convey depth of lower levels! Will affect 3+


@dataclass
class MinimaxGuess:

    word: Word
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
        return str(self.word)

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
    def __init__(self, histogram_builder: HistogramBuilder) -> None:
        self.hist_builder = histogram_builder

    def get_best_guess(self, all_words: WordSeries, potential_solns: WordSeries) -> EntropyGuess:
        return min(self.all_guesses(all_words, potential_solns))

    def all_guesses(self, all_words: WordSeries, potential_solns: WordSeries) -> Iterator[EntropyGuess]:

        if len(potential_solns) <= 2:
            yield EntropyGuess(potential_solns.words[0], True, 1)
        else:
            yield from self.hist_builder.stream(all_words, potential_solns, self._create_guess)

    @property
    def all_seeds(self) -> list[Word]:
        seeds = {"OLEA", "RAISE", "TAILER", "TENAILS", "CENTRALS", "SECRETION"}
        return [Word(seed) for seed in seeds]

    @staticmethod
    def _create_guess(word: Word, is_common_word: bool, histogram: np.ndarray) -> EntropyGuess:

        counts = histogram[histogram > 0]
        probabilites = counts / np.sum(counts)
        entropy = -probabilites.dot(np.log2(probabilites))

        return EntropyGuess(word, is_common_word, entropy)


class DeepEntropySolver(EntropySolver):
    def __init__(self, histogram_builder: HistogramBuilder, inner_solver: EntropySolver) -> None:
        super().__init__(histogram_builder)
        self.inner = inner_solver

    def get_best_guess(self, all_words: WordSeries, potential_solns: WordSeries) -> EntropyGuess:

        N_GUESSES = 10

        guesses = self.all_guesses(all_words, potential_solns)
        best_guesses = sorted(guesses)[:N_GUESSES]
        deep_guesses: list[EntropyGuess] = []

        for guess in best_guesses:
            solns_by_outcome = self.hist_builder.get_solns_by_score(potential_solns, guess.word)

            if guess.is_common_word and all(len(s) == 1 for s in solns_by_outcome.values()):
                return guess

            avg_entropy_reduction = 0.0
            for nested_potential_solns in solns_by_outcome.values():
                probability = len(nested_potential_solns) / len(potential_solns)
                nested_best_guess = self.inner.get_best_guess(all_words, nested_potential_solns)
                entropy_reduction = nested_best_guess.entropy * probability
                avg_entropy_reduction += entropy_reduction
            deep_guesses.append(guess + avg_entropy_reduction)

        deep_best_guess = min(deep_guesses)  # TODO not good enough. Where there are ties, look up!
        return deep_best_guess


@dataclass
class EntropyGuess:

    word: Word
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
