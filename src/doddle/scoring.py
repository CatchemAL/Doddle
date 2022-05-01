import numpy as np
from numba import int8, int32, jit  # type: ignore

from .words import Word


class Scorer:
    """A class to score a guess given a solution."""

    __slots__ = ["size", "_powers"]

    def __init__(self, size: int = 5) -> None:
        """Initialises a new instance of a Scorer.

        Args:
            size (int, optional): The word length. Defaults to 5.
        """
        self.size = size
        self._powers = (3 ** np.arange(size - 1, -1, -1)).astype(np.int32)

    @property
    def perfect_score(self) -> int:
        """A decimal representation of the perfect ternary score.

        e.g. in a 5 letter game of Wordle, the perfect score is 22222.
        Therefore, this method would return 242.

        Returns:
            int: Returns the perfect score.
        """
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
        """Calculates a score given a solution and a guess.

        The score is a decimal representation of a ternary score. By ternary
        score, we assume that:
         - 0 is an unmatched letter
         - 1 is a partial match
         - 2 is a perfectly matched score

        Example:

        Guess: SNAKE
        Soln.: SHARK
        Score: 20210   <-- This is the ternary representation of the score

        As the decimal (base 10) representation of this ternary (base 3) number
        is 183, we return 183. The advantage of returning a decimal number is
        that we map all scores in, say, a 5 letter game to a *dense* set of 242
        unique scores. This allows for fast indexing over dictionary lookups.

        Args:
            solution (Word): The solution to the game.
            guess (Word): The guess.

        Returns:
            int: The score.
        """
        # return score_word_slow(solution.value, guess.value) # (x50 slower!)
        return _score_word_jit(solution.vector, guess.vector, self._powers)


@jit(int32(int8[:], int8[:], int32[:]), nopython=True)
def _score_word_jit(solution_array: np.ndarray, guess_array: np.ndarray, powers: np.ndarray) -> int:
    """Optimised internal call to score a word. See Solver.score_word(...) for details."""

    matches = solution_array == guess_array

    value = 0
    for (i, is_match) in enumerate(matches):
        if is_match:
            value += 1
    value *= 10

    approx = 0
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
        approx += int(is_partial_match)

    return value + approx


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
    """Converts a ternary number to its decimal (base 10) equivalent.

    Args:
        ternary (str): The ternary score.

    Returns:
        int: The decimal score.
    """
    value = 0
    digits = (int(digit) for digit in reversed(list(ternary)))
    for i, num in enumerate(digits):
        value += num * (3**i)
    return value


def to_ternary(score: int, size: int) -> str:
    """Converts a decimal number to its ternary (base 3) equivalent.

    Args:
        score (int): The decimal score.
        size (int): The word length.

    Returns:
        str: The ternary score.
    """
    return np.base_repr(score, base=3).zfill(size)
