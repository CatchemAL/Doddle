from __future__ import annotations

import abc
from typing import Generic, Iterator, TypeVar

import numpy as np

from .guess import EntropyGuess, MinimaxGuess
from .histogram import Guess, HistogramBuilder
from .words import Word, WordSeries

TGuess = TypeVar("TGuess", bound=Guess)


class Solver(Generic[TGuess], abc.ABC):
    @abc.abstractmethod
    def get_best_guess(self, all_words: WordSeries, potential_solns: WordSeries) -> TGuess:
        """Gets the best guess to play given two lists:
         - the full series of all_words that could possibly be played;
         - the series of potential_solns left to search (i.e. the words that have yet to
           be ruled out by the solver).

        Args:
          all_words (WordSeries): The full universe of words.
          potential_solns (WordSeries): The words that still remain as potential solutions.

        Returns:
          Guess: Any object that implements the guess protocol.
        """
        pass

    @property
    @abc.abstractmethod
    def all_seeds(self) -> list[Word]:
        """Returns a list of all seeds for words of length 4-9.

        Returns:
          list[Word]: The list of all seeds.
        """
        pass

    def seed(self, size: int) -> Word:
        """Gets the optimal starting word to use for a given solver
        implementation. This is for efficiency purposes - there's no
        need to compute the opening move from first principles as it
        will be the same each time.

        Args:
          size (int): The word length of the seed.

        Returns:
          Word: The seed.
        """
        seed_by_size = {len(word): word for word in self.all_seeds}
        return seed_by_size[size]


class MinimaxSolver(Solver[MinimaxGuess]):
    def __init__(self, histogram_builder: HistogramBuilder) -> None:
        self.hist_builder = histogram_builder

    def get_best_guess(self, all_words: WordSeries, potential_solns: WordSeries) -> MinimaxGuess:
        """See base class."""
        all_guesses = self.all_guesses(all_words, potential_solns)
        return min(all_guesses)

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
        """See base class."""

        N_GUESSES = 50
        N_BRANCHES = 10

        guesses = self.all_guesses(all_words, potential_solns)
        best_guesses = sorted(guesses)[:N_GUESSES]

        deep_worst_best_guess_by_guess: dict[Word, MinimaxGuess] = {}

        for guess in best_guesses:
            # TODO If perfect guess...
            solns_by_score = self.hist_builder.get_solns_by_score(potential_solns, guess.word)
            worst_outcomes = sorted(solns_by_score, key=lambda s: -len(solns_by_score[s]))
            nested_best_guesses: list[MinimaxGuess] = []
            for worst_outcome in worst_outcomes[:N_BRANCHES]:
                nested_potential_solns = solns_by_score[worst_outcome]
                nested_best_guess = self.inner.get_best_guess(all_words, nested_potential_solns)
                nested_best_guesses.append(nested_best_guess)
            worst_best_guess = max(nested_best_guesses)
            deep_worst_best_guess_by_guess[guess.word] = worst_best_guess

        def get_guess_given_word(word: Word) -> MinimaxGuess:
            return deep_worst_best_guess_by_guess[word]

        best_guess_str = min(deep_worst_best_guess_by_guess, key=get_guess_given_word)
        best_guess = next(guess for guess in best_guesses if guess.word == best_guess_str)
        return best_guess  # TODO bug. Guess needs to convey depth of lower levels! Will affect 3+


class EntropySolver(Solver[EntropyGuess]):
    def __init__(self, histogram_builder: HistogramBuilder) -> None:
        self.hist_builder = histogram_builder

    def get_best_guess(self, all_words: WordSeries, potential_solns: WordSeries) -> EntropyGuess:
        """See base class."""
        all_guesses = self.all_guesses(all_words, potential_solns)
        return min(all_guesses)

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
        """See base class."""

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
