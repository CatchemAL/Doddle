import numpy as np
from numba import int8, int32, jit  # type: ignore

from .words import Word


class Scorer:
    __slots__ = ["size", "_powers"]

    def __init__(self, size: int = 5) -> None:
        self.size = size
        self._powers = (3 ** np.arange(size - 1, -1, -1)).astype(np.int32)

    @property
    def perfect_score(self) -> int:
        return (3**self.size) - 1

    def is_perfect_score(self, score: int) -> bool:
        """Returns true if the score provided results in the game being won.

        Args:
            score (int): The decimal representation of a ternary number.

        Returns:
            bool: A bool denoting whether the score is a perfect score.
        """
        return score == self.perfect_score

    def score_word(self, solution: Word, guess: Word) -> int:
        # return score_word_slow(solution.value, guess.value) # (x50 slower!)
        return score_word_jit(solution.vector, guess.vector, self._powers)


@jit(int32(int8[:], int8[:], int32[:]), nopython=True)
def score_word_jit(solution_array: np.ndarray, guess_array: np.ndarray, powers: np.ndarray) -> int:

    matches = solution_array == guess_array

    value = 0
    for (i, is_match) in enumerate(matches):
        if is_match:
            value += 2 * powers[i]

    for (i, is_match) in enumerate(matches):
        if is_match:
            continue

        letter = guess_array[i]
        num_times_already_observed = 0
        for j in range(i):
            if not matches[j]:
                num_times_already_observed += letter == guess_array[j]

        num_times_in_solution = 0
        for (j, is_match_j) in enumerate(matches):
            if is_match_j:
                continue
            soln_letter = solution_array[j]
            num_times_in_solution += int(letter == soln_letter)

        is_partial_match = num_times_already_observed < num_times_in_solution
        value += int(powers[i] * is_partial_match)

    return value


def score_word_slow(soln: str, guess: str) -> int:
    """
    This is no longer used but is kept because it is a more
    readable reference implementation of the above, more
    optimised code.
    """
    size = len(soln)
    solution_array = np.array(list(soln))
    guess_array = np.array(list(guess))

    indices = np.arange(size, 0, -1) - 1
    powers = 3**indices

    # First we tackle exact matches
    matches = solution_array == guess_array
    value = powers[matches].sum() * 2

    # Remove exact matches from the search
    unmatched = ~matches
    unmatched_powers = powers[unmatched]
    unmatched_solution = solution_array[unmatched]
    unmatched_guess = guess_array[unmatched]

    partial_matches = unmatched_powers == -1

    for i in range(len(unmatched_powers)):
        letter = unmatched_guess[i]
        num_times_already_observed = np.sum(letter == unmatched_guess[:i])
        num_times_in_solution = np.sum(letter == unmatched_solution)
        is_partial_match = num_times_already_observed < num_times_in_solution
        partial_matches[i] = is_partial_match

    value += unmatched_powers[partial_matches].sum()
    return value


def from_ternary(ternary: str) -> int:
    value = 0
    digits = (int(digit) for digit in reversed(list(ternary)))
    for i, num in enumerate(digits):
        value += num * (3**i)
    return value


def to_ternary(score: int, size: int) -> str:
    return np.base_repr(score, base=3).zfill(size)
