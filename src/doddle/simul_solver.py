from __future__ import annotations

import abc
from typing import Generic, Iterator, TypeVar

import numpy as np

from .game import Game, SimultaneousGame
from .guess import EntropyGuess, Guess, MinimaxGuess, MinimaxSimulGuess
from .histogram import HistogramBuilder, to_histogram
from .words import Word, WordSeries

TSingleGuess = TypeVar("TSingleGuess", bound=Guess)
TSimulGuess = TypeVar("TSimulGuess", bound=Guess)


class SimulSolver(Generic[TSingleGuess, TSimulGuess], abc.ABC):
    def __init__(self, hist_builder: HistogramBuilder) -> None:
        self.hist_builder = hist_builder

    def get_best_guess(self, all_words: WordSeries, games: SimultaneousGame) -> TSimulGuess:

        for game in games:
            if game.is_solved or len(game.potential_solns) > 1:
                continue

            word: Word = game.potential_solns.words[0]
            solns_by_score = self.hist_builder.get_solns_by_score(game.potential_solns, word)
            histogram = to_histogram(solns_by_score)
            single_guess = self.single_guess(word, True, histogram)
            return self.to_simul_guess([game], (single_guess,))

        all_guesses = self.all_guesses(all_words, games)
        return min(all_guesses)

    def all_guesses(self, all_words: WordSeries, games: SimultaneousGame) -> Iterator[TSimulGuess]:

        unsolved_games = [game for game in games if not game.is_solved]
        guess_streams: list[Iterator[TSingleGuess]] = []
        for game in unsolved_games:
            stream = self.hist_builder.stream(all_words, game.potential_solns, self.single_guess)
            guess_streams.append(stream)

        for guess_tuple in zip(*guess_streams):
            simul_guess = self.to_simul_guess(unsolved_games, guess_tuple)
            yield simul_guess

    @abc.abstractmethod
    def single_guess(self, guess: Word, is_potential_soln: bool, histogram: np.ndarray) -> TSingleGuess:
        ...

    @abc.abstractmethod
    def to_simul_guess(self, games: list[Game], single_guesses: tuple[TSingleGuess]) -> TSimulGuess:
        ...

    @property
    @abc.abstractmethod
    def all_seeds(self) -> list[Word]:
        ...

    def seed(self, size: int) -> Word:
        seed_by_size = {len(word): word for word in self.all_seeds}
        return seed_by_size[size]


class MinimaxSimulSolver(SimulSolver[MinimaxGuess, MinimaxSimulGuess]):
    def __init__(self, histogram_builder: HistogramBuilder) -> None:
        self.hist_builder = histogram_builder

    def single_guess(self, guess: Word, is_potential_soln: bool, histogram: np.ndarray) -> MinimaxGuess:
        return MinimaxGuess.from_histogram(guess, is_potential_soln, histogram)

    def to_simul_guess(self, games: list[Game], guess_tuple: tuple[MinimaxGuess]) -> MinimaxSimulGuess:

        word = guess_tuple[0].word
        eligibility_count = len([guess for guess in guess_tuple if guess.is_common_word])
        is_common_word = eligibility_count > 0
        largest_sizes = np.array([g.size_of_largest_bucket for g in guess_tuple])
        num_solutions = np.array([len(g.potential_solns) for g in games])
        num_buckets = sum([g.number_of_buckets for g in guess_tuple])
        largest_sizes_pct = largest_sizes / num_solutions
        tot = largest_sizes.sum()
        min = largest_sizes.min()
        max = largest_sizes.max()
        pct_left = np.prod(largest_sizes_pct)

        return MinimaxSimulGuess(word, is_common_word, pct_left, min, tot, max, num_buckets)

    @property
    def all_seeds(self) -> list[Word]:
        seeds = {"OLEA", "RAISE", "TAILER", "TENAILS", "CENTRALS", "SECRETION"}
        return [Word(seed) for seed in seeds]


class EntropySimulSolver(SimulSolver[EntropyGuess, EntropyGuess]):
    def __init__(self, histogram_builder: HistogramBuilder) -> None:
        self.hist_builder = histogram_builder

    def single_guess(self, guess: Word, is_potential_soln: bool, histogram: np.ndarray) -> EntropyGuess:
        return EntropyGuess.from_histogram(guess, is_potential_soln, histogram)

    def to_simul_guess(self, games: list[Game], guess_tuple: tuple[EntropyGuess]) -> EntropyGuess:
        word = guess_tuple[0].word
        eligibility_count = len([guess for guess in guess_tuple if guess.is_common_word])
        is_common_word = eligibility_count > 0
        entropies = np.array([g.entropy for g in guess_tuple])
        total_entropy = sum(entropies)

        return EntropyGuess(word, is_common_word, total_entropy)

    @property
    def all_seeds(self) -> list[Word]:
        seeds = {"OLEA", "RAISE", "TAILER", "TENAILS", "CENTRALS", "SECRETION"}
        return [Word(seed) for seed in seeds]
