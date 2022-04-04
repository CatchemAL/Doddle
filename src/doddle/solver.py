from __future__ import annotations

import abc
from typing import Generic, Iterator, TypeVar

import numpy as np

from .guess import EntropyGuess, Guess, MinimaxGuess
from .histogram import HistogramBuilder, to_histogram
from .words import Word, WordSeries

TGuess_co = TypeVar("TGuess_co", bound=Guess, covariant=True)


class Solver(Generic[TGuess_co], abc.ABC):
    def __init__(self, hist_builder: HistogramBuilder) -> None:
        self.hist_builder = hist_builder

    def get_best_guess(self, all_words: WordSeries, potential_solns: WordSeries) -> TGuess_co:
        """Gets the best guess to play given two lists:
         - the full series of all_words that could possibly be played;
         - the series of potential_solns left to search (i.e. the words that have yet to
           be ruled out by the solver).

        Args:
          all_words (WordSeries): The full universe of words.
          potential_solns (WordSeries): The words that still remain as potential solutions.

        Returns:
          Guess: The guess object implementing the guess protocol
        """
        if len(potential_solns) <= 2:
            guess = potential_solns.words[0]
            solns_by_score = self.hist_builder.get_solns_by_score(potential_solns, guess)
            histogram = to_histogram(solns_by_score)
            return self._build_guess(guess, True, histogram)

        all_guesses = self.all_guesses(all_words, potential_solns)
        return min(all_guesses)

    def all_guesses(self, all_words: WordSeries, potential_solns: WordSeries) -> Iterator[TGuess_co]:
        """Yields a stream of guesses based on the full universe of available words.

        Args:
            all_words (WordSeries): The full universe of words.
            potential_solns (WordSeries): The words that still remain as potential solutions.

        Yields:
            Iterator[TGuess]: The guess object implementing the guess protocol
        """
        yield from self.hist_builder.stream(all_words, potential_solns, self._build_guess)

    @abc.abstractmethod
    def _build_guess(self, word: Word, is_potential_soln: bool, histogram: np.ndarray) -> TGuess_co:
        """Factory method for building a guess from a histogram

        Args:
            word (Word): The word that was guessed
            is_potential_soln (bool): Whether the word could possibly be a solution
            histogram (np.ndarray): The associated histogram in optimised, vector form.

        Returns:
            TGuess: The guess object implementing the guess protocol
        """
        ...  # pragma: no cover

    @property
    @abc.abstractmethod
    def all_seeds(self) -> list[Word]:
        """Returns a list of all seeds for words of length 4-9.

        Returns:
          list[Word]: The list of all seeds.
        """
        ...  # pragma: no cover

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
        super().__init__(histogram_builder)

    @property
    def all_seeds(self) -> list[Word]:
        """See base class."""
        seeds = ["OLEA", "RAISE", "TAILER", "TENAILS", "CENTRALS", "SECRETION"]
        return [Word(seed) for seed in seeds]

    def _build_guess(self, word: Word, is_potential_soln: bool, histogram: np.ndarray) -> MinimaxGuess:
        """See base class."""
        return MinimaxGuess.from_histogram(word, is_potential_soln, histogram)


class DeepMinimaxSolver(MinimaxSolver):
    def __init__(self, histogram_builder: HistogramBuilder, inner_solver: MinimaxSolver) -> None:
        super().__init__(histogram_builder)
        self.inner = inner_solver

    def get_best_guess(self, all_words: WordSeries, potential_solns: WordSeries) -> MinimaxGuess:
        """See base class."""

        N_GUESSES = 50
        N_BRANCHES = 10

        if len(potential_solns) <= 2:
            return super().get_best_guess(all_words, potential_solns)

        guesses = self.all_guesses(all_words, potential_solns)
        best_guesses = sorted(guesses)[:N_GUESSES]

        combined_guesses: list[MinimaxGuess] = []
        for guess in best_guesses:
            if guess.perfectly_partitions():
                return MinimaxGuess(guess.word, guess.is_potential_soln, 0, 0)

            solns_by_score = self.hist_builder.get_solns_by_score(potential_solns, guess.word)
            worst_scores = sorted(solns_by_score, key=lambda s: -len(solns_by_score[s]))
            best_deep_guesses: list[MinimaxGuess] = []
            for worst_score in worst_scores[:N_BRANCHES]:
                potential_deep_solns = solns_by_score[worst_score]
                deep_guess = self.inner.get_best_guess(all_words, potential_deep_solns)
                best_deep_guesses.append(deep_guess)
            worst_best_deep_guess = max(best_deep_guesses)
            combined_guess = guess >> worst_best_deep_guess
            combined_guesses.append(combined_guess)

        return min(combined_guesses)


class EntropySolver(Solver[EntropyGuess]):
    def __init__(self, histogram_builder: HistogramBuilder) -> None:
        super().__init__(histogram_builder)

    @property
    def all_seeds(self) -> list[Word]:
        """See base class."""
        seeds = ["OLEA", "RAISE", "TAILER", "TENAILS", "CENTRALS", "SECRETION"]
        return [Word(seed) for seed in seeds]

    def _build_guess(self, word: Word, is_potential_soln: bool, histogram: np.ndarray) -> EntropyGuess:
        """See base class."""
        return EntropyGuess.from_histogram(word, is_potential_soln, histogram)


class DeepEntropySolver(EntropySolver):
    def __init__(self, histogram_builder: HistogramBuilder, inner_solver: EntropySolver) -> None:
        super().__init__(histogram_builder)
        self.inner = inner_solver

    def get_best_guess(self, all_words: WordSeries, potential_solns: WordSeries) -> EntropyGuess:
        """See base class."""

        N_GUESSES = 10

        if len(potential_solns) <= 2:
            return super().get_best_guess(all_words, potential_solns)

        guesses = self.all_guesses(all_words, potential_solns)
        best_guesses = sorted(guesses)[:N_GUESSES]

        combined_guesses: list[EntropyGuess] = []
        for guess in best_guesses:
            solns_by_score = self.hist_builder.get_solns_by_score(potential_solns, guess.word)

            if max(len(s) for s in solns_by_score.values()) == 1:
                return EntropyGuess(guess.word, guess.is_potential_soln, float("inf"))

            avg_entropy_reduction = 0.0
            for potential_deep_solns in solns_by_score.values():
                probability = len(potential_deep_solns) / len(potential_solns)
                deep_guess = self.inner.get_best_guess(all_words, potential_deep_solns)
                entropy_reduction = deep_guess.entropy * probability
                avg_entropy_reduction += entropy_reduction
            combined_guess = guess + avg_entropy_reduction
            combined_guesses.append(combined_guess)

        # TODO If multiple guesses solve the problem in two steps, ideally
        # we want the guess that had the greatest entropy reduction at step
        # one. Right now it will go by potential solution, then alphabetical
        deep_best_guess = min(combined_guesses)
        return deep_best_guess
