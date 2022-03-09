from __future__ import annotations

import abc
from typing import Iterator

import numpy as np

from .game import SimultaneousGame
from .guess import Guess, MinimaxGuess, MinimaxSimulGuess
from .histogram import HistogramBuilder
from .solver import MinimaxSolver
from .words import Word, WordSeries


class SimulSolver(abc.ABC):
    @abc.abstractmethod
    def get_best_guess(self, all_words: WordSeries, game: SimultaneousGame) -> Guess:
        ...

    @property
    @abc.abstractmethod
    def all_seeds(self) -> list[Word]:
        ...

    def seed(self, size: int) -> Word:
        seed_by_size = {len(word): word for word in self.all_seeds}
        return seed_by_size[size]


class MinimaxSimulSolver(SimulSolver):
    def __init__(self, histogram_builder: HistogramBuilder) -> None:
        self.hist_builder = histogram_builder

    def get_best_guess(self, all_words: WordSeries, game: SimultaneousGame) -> Guess:
        return min(self.all_guesses(all_words, game))

    def all_guesses(self, all_words: WordSeries, games: SimultaneousGame) -> Iterator[MinimaxSimulGuess]:

        potential_solns_list = [game.potential_solns for game in games if not game.is_solved]
        for potential_solns in potential_solns_list:
            if len(potential_solns) == 1:
                word: Word = potential_solns.words[0]
                yield MinimaxSimulGuess(word, True, 1, 1, 1, 1, 1)
                return

        guess_streams: list[Iterator[MinimaxGuess]] = []
        for potential_solns in potential_solns_list:
            stream = self.hist_builder.stream(all_words, potential_solns, MinimaxSolver._create_guess)
            guess_streams.append(stream)

        num_solutions = np.array([len(potential_solns) for potential_solns in potential_solns_list])
        for guess_tuple in zip(*guess_streams):
            word = guess_tuple[0].word
            eligibility_count = len([guess for guess in guess_tuple if guess.is_common_word])
            is_common_word = eligibility_count > 0
            largest_sizes = np.array([g.size_of_largest_bucket for g in guess_tuple])
            num_buckets = sum([g.number_of_buckets for g in guess_tuple])
            largest_sizes_pct = largest_sizes / num_solutions
            tot = largest_sizes.sum()
            min = largest_sizes.min()
            max = largest_sizes.max()
            pct_left = np.prod(largest_sizes_pct)

            yield MinimaxSimulGuess(word, is_common_word, pct_left, min, tot, max, num_buckets)

    @property
    def all_seeds(self) -> list[Word]:
        seeds = {"OLEA", "RAISE", "TAILER", "TENAILS", "CENTRALS", "SECRETION"}
        return [Word(seed) for seed in seeds]
