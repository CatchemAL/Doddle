from __future__ import annotations

from typing import Callable, Protocol, TypeVar

import numpy as np
from numba import njit

from .scoring import Scorer
from .words import Word, WordSeries


class Guess(Protocol):
    word: str
    is_common_word: bool


TGuess = TypeVar("TGuess", bound=Guess)


class HistogramBuilder:
    def __init__(
        self, scorer: Scorer, potential_solns: WordSeries, all_words: WordSeries, lazy_eval: bool = True
    ) -> None:
        self.score_matrix = ScoreMatrix(scorer, potential_solns, all_words, lazy_eval)
        self.scorer = scorer

    def get_solns_by_score(self, potential_solns: WordSeries, guess: Word) -> dict[int, WordSeries]:

        score_func = np.vectorize(self.scorer.score_word)
        scores = score_func(potential_solns.words, guess)
        unique_scores, positions = np.unique(scores, return_inverse=True)

        solns_by_score: dict[int, WordSeries] = {}
        for (i, unique_score) in enumerate(unique_scores):
            maps_to_score = positions == i
            filtered_solns = potential_solns[maps_to_score]
            solns_by_score[unique_score] = filtered_solns

        return solns_by_score

    def stream(
        self,
        potential_solns: WordSeries,
        all_words: WordSeries,
        guess_factory: Callable[[Word, bool, np.ndarray], TGuess],
    ) -> TGuess:

        # First, we precompute the scores for all remaining solutions
        self.score_matrix.precompute(potential_solns)

        # Efficiently flag words that could feasibly be a solution
        indices = all_words.find_index(potential_solns.words)
        is_common = np.zeros(len(all_words), dtype=bool)
        is_common[indices] = True

        scores = self.score_matrix.storage[:, potential_solns.index]

        histogram = self.allocate_histogram_vector(all_words.word_length)
        for i, word in enumerate(all_words):
            populate_histogram(scores, i, histogram)
            yield guess_factory(word, is_common[i], histogram)

    @staticmethod
    def allocate_histogram_vector(word_length: int) -> np.ndarray:
        return np.zeros(3**word_length, dtype=int)


@njit
def populate_histogram(matrix: np.ndarray, row: int, hist: np.ndarray) -> None:
    hist[:] = 0
    for j in range(matrix.shape[1]):
        idx = matrix[row, j]
        hist[idx] += 1


class ScoreMatrix:
    def __init__(
        self, scorer: Scorer, potential_solns: WordSeries, all_words: WordSeries, lazy_eval: bool = True
    ) -> None:
        self.scorer = scorer
        self.potential_solns = potential_solns
        self.all_words = all_words

        rows, cols = all_words.index.max() + 1, potential_solns.index.max() + 1
        self.is_calculated = np.zeros(cols, dtype=bool)
        self.storage = np.full((rows, cols), -1, dtype=int)
        self.is_fully_initialized = False

        if not lazy_eval:
            self.precompute(potential_solns)

    def precompute(self, potential_solns: WordSeries | None = None) -> None:

        solns = potential_solns or self.potential_solns
        if self.is_fully_initialized or np.all(self.is_calculated[solns.index]):
            return

        row_words = self.all_words.words[:, np.newaxis]
        col_words = solns.words[np.newaxis, :]

        func = np.vectorize(self.scorer.score_word)
        self.storage[:, solns.index] = func(row_words, col_words)
        self.is_calculated[solns.index] = True
        self.is_fully_initialized = np.all(self.is_calculated)
