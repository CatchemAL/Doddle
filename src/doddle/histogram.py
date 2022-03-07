from __future__ import annotations

from typing import Callable, Iterator, TypeVar

import numpy as np
from numba import njit  # type: ignore

from .guess import Guess
from .scoring import Scorer
from .words import Word, WordSeries

TGuess = TypeVar("TGuess", bound=Guess)


class HistogramBuilder:
    """
    The class responsible for creating a histogram (or streaming many histograms)
    given a guess or sequence of guesses.

    The histogram is a fundamental to the solve. If we know how any guess fractures the
    remaining solution space, we can choose the guess that minimises an objective function.
    All Doddle solvers are heuristic and rely on knowledge of the histogram produced from
    each guess.
    """

    def __init__(
        self, scorer: Scorer, all_words: WordSeries, potential_solns: WordSeries, lazy_eval: bool = True
    ) -> None:
        """Initialises a new instance of a HistogramBuilder

        Args:
          scorer (Scorer):
            The scorer

          all_words (WordSeries):
            All words that Doddle could possibly accept.

          potential_solns (WordSeries):
            The list of solutions that could be answers.

          lazy_eval (bool, optional):
            Whether to pre-compute the score matrix. The score matrix scores every
            word, as a guess, against every word, as a solution and computes the
            score you should observe. Lazy evaluation results in quick initialisation
            but slower solves. Disabling this feature is recommended if you inted to
            perform multiple runs. Defaults to True.
        """

        self.score_matrix = ScoreMatrix(scorer, all_words, potential_solns, lazy_eval)
        self.scorer = scorer

    def get_solns_by_score(self, potential_solns: WordSeries, guess: Word) -> dict[int, WordSeries]:
        """Gets a histogram of all the remaining solutions bucketed by score given a guess.

        Args:
            potential_solns (WordSeries): The remaining words that could be a solution.
            guess (Word): The guess.

        Returns:
            dict[int, WordSeries]: A dictionary of potential solutions, partitioned by score.
        """

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
        all_words: WordSeries,
        potential_solns: WordSeries,
        guess_factory: Callable[[Word, bool, np.ndarray], TGuess],
    ) -> Iterator[TGuess]:
        """Yields a sequences of guesses constructed via a user-defined factory method.

        Each guess is formed from the histogram of bucketed solutions.

        Args:
          all_words (WordSeries): 
            The list of all words that could be guessed
          
          potential_solns (WordSeries):
            The remaining words that could be solutions

          guess_factory (Callable[[Word, bool, np.ndarray], TGuess]):
            A factory method for producing a guess. The guess is formed from three
            parameters:
            1) The guessed Word
            2) A flag denoting whether that word could be a potential solution
            3) A histogram of solutions bucketed by score

        Yields:
          Iterator[TGuess]:
            A guess produced via the factory method.
        """

        # First, we precompute the scores for all remaining solutions
        self.score_matrix.precompute(potential_solns)

        # Efficiently flag words that could feasibly be a solution
        indices = all_words.find_index(potential_solns.words)
        is_common = np.zeros(len(all_words), dtype=bool)
        is_common[indices] = True

        scores = self.score_matrix.storage[:, potential_solns.index]

        histogram = self._allocate_histogram_vector(all_words.word_length)
        for i, word in enumerate(all_words):
            _populate_histogram(scores, i, histogram)
            yield guess_factory(word, is_common[i], histogram)

    @staticmethod
    def _allocate_histogram_vector(word_length: int) -> np.ndarray:
        """Allocates a vector that can be recycled.

        Args:
            word_length (int): The word length of the game.

        Returns:
            np.ndarray: The allocated vector.
        """
        return np.zeros(3**word_length, dtype=int)


@njit
def _populate_histogram(matrix: np.ndarray, row: int, hist: np.ndarray) -> None:
    """Aggressive optimisation of the histogram creation.

    This is performance critical code. Here, we use a preallocated vector
    rather than instantiating one for each guess. Instead of using a dictionary,
    we use fast indexing to build out the histogram. Each index in the vector
    represents a score.

    Hence the reason we use a decimal representation of each ternary score - we
    need a desnre representation of the score to build an efficient histogram.

    Args:
        matrix (np.ndarray): The internal, precomputed score matrix
        row (int): The row in the score matrix corresponding to a guess
        hist (np.ndarray): The preallocated histogram vector
    """
    hist[:] = 0
    for j in range(matrix.shape[1]):
        idx = matrix[row, j]
        hist[idx] += 1


class ScoreMatrix:
    """
    Internal storage of all words scored against all words.

    This matrix is used as an optimsation to avoid rescoring the same
    words multiple times within a solve and is particularly important 
    for deep searches.

    The rows in the matrix correspond to all possible words. The columns
    correspond to the words that could ever be answers.
    """

    def __init__(
        self, scorer: Scorer, all_words: WordSeries, potential_solns: WordSeries, lazy_eval: bool = True
    ) -> None:
        """Initialises a new instance of the score matrix.

        Args:
            scorer (Scorer): The scorer.
            all_words (WordSeries): All possible words in the Doddle dictionary.
            potential_solns (WordSeries): All words that could be a solution.
            lazy_eval (bool, optional): Whether to perform lazy evaluation of each score. Defaults to True.
        """
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
        """Method to precompute the score matrix.

        Args:
            potential_solns (WordSeries | None, optional):
                The potnetial solutions to compute upfront. Defaults to None.
        """

        solns = potential_solns or self.potential_solns
        if self.is_fully_initialized or np.all(self.is_calculated[solns.index]):
            return

        row_words = self.all_words.words[np.newaxis, :]
        col_words = solns.words[:, np.newaxis]

        # TODO investigate performance of np.vectorize
        func = np.vectorize(self.scorer.score_word)
        self.storage[:, solns.index] = func(col_words, row_words).T
        self.is_calculated[solns.index] = True
        self.is_fully_initialized = bool(np.all(self.is_calculated))
