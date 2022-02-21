from __future__ import annotations

from typing import Iterator

import numpy as np

from .guess import MinimaxGuess, QuordleGuess
from .histogram import HistogramBuilder
from .words import Word, WordSeries


class QuordleGame:
    def __init__(self, available_answers: WordSeries, soln: Word | None = None) -> None:
        self.available_answers = available_answers
        self.soln = soln
        self.is_solved = False
        self.guesses_to_solve = -1

    def __repr__(self) -> str:

        soln = self.soln if self.soln else Word("?" * self.available_answers.word_length)

        if self.is_solved:
            message = f"solved in {self.guesses_to_solve} guesses"
        else:
            message = f"unsolved - {len(self.available_answers)} possible solutions"

        return f"{soln} ({message})"

    @staticmethod
    def games(available_answers: WordSeries, solns: list[Word]) -> list[QuordleGame]:
        return [QuordleGame(available_answers, soln) for soln in solns]


class QuordleSolver:
    def __init__(self, histogram_builder: HistogramBuilder) -> None:
        self.hist_builder = histogram_builder

    # TODO: potentially an implict vs explicit implementation
    def get_best_guess(self, all_words: WordSeries, games: list[QuordleGame]) -> MinimaxGuess:
        return min(self.all_guesses(all_words, games))

    def all_guesses(self, all_words: WordSeries, games: list[QuordleGame]) -> Iterator[MinimaxGuess]:

        potential_solns_list = [game.available_answers for game in games if not game.is_solved]
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
