from __future__ import annotations

from typing import Iterator

import numpy as np

from .game import SimultaneousGame
from .guess import MinimaxGuess, QuordleGuess
from .histogram import HistogramBuilder
from .words import Word, WordSeries


class QuordleSolver:
    def __init__(self, histogram_builder: HistogramBuilder) -> None:
        self.hist_builder = histogram_builder

    # TODO: potentially an implict vs explicit implementation
    def get_best_guess(self, all_words: WordSeries, games: SimultaneousGame) -> QuordleGuess:
        return min(self.all_guesses(all_words, games))

    def seed(self, size: int) -> Word:
        seed_by_size = {len(word): word for word in self.all_seeds}
        return seed_by_size[size]

    def all_guesses(self, all_words: WordSeries, games: SimultaneousGame) -> Iterator[QuordleGuess]:

        potential_solns_list = [game.potential_solns for game in games if not game.is_solved]
        for potential_solns in potential_solns_list:
            if len(potential_solns) == 1:
                yield QuordleGuess(potential_solns.words[0], True, 1, 1, 1, 1, 1, 1, 1, 1)
                return

        streams: list[Iterator[MinimaxGuess]] = []
        for potential_solns in potential_solns_list:
            stream = self.hist_builder.stream(all_words, potential_solns, self._create_guess)
            streams.append(stream)

        num_solutions = np.array([len(potential_solns) for potential_solns in potential_solns_list])
        for quad_guess in zip(*streams):
            guessed_word = quad_guess[0].word
            is_common_word = quad_guess[0].is_common_word
            largest_sizes = np.array([g.size_of_largest_bucket for g in quad_guess])
            num_buckets = sum([g.number_of_buckets for g in quad_guess])
            largest_sizes_pct = largest_sizes / num_solutions
            sum_abs = sum(largest_sizes)
            min_abs = min(largest_sizes)
            max_abs = max(largest_sizes)
            sum_pct = sum(largest_sizes_pct)
            min_pct = min(largest_sizes_pct)
            max_pct = max(largest_sizes_pct)
            pct_product = sum(largest_sizes_pct**4)

            yield QuordleGuess(
                guessed_word,
                is_common_word,
                sum_abs,
                min_abs,
                max_abs,
                sum_pct,
                min_pct,
                max_pct,
                pct_product,
                num_buckets,
            )

    @property
    def all_seeds(self) -> list[Word]:
        seeds = {"OLEA", "RAISE", "TAILER", "TENAILS", "CENTRALS", "SECRETION"}
        return [Word(seed) for seed in seeds]

    @staticmethod
    def _create_guess(word: Word, is_common_word: bool, histogram: np.ndarray) -> MinimaxGuess:
        num_buckets = np.count_nonzero(histogram)
        size_of_largest_bucket = histogram.max()
        return MinimaxGuess(word, is_common_word, num_buckets, size_of_largest_bucket)
