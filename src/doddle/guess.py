from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Protocol

import numpy as np

from .words import Word


class Guess(Protocol):  # pragma: no cover
    """Strucural protocol for a guess."""

    @property
    def word(self) -> Word:
        """The guessed word.

        Returns:
          Word:
            Returns the guessed word
        """
        ...

    @property
    def is_potential_soln(self) -> bool:
        """Whether the word is a possible answer.

        Returns:
          bool:
            Returns whether the word is a possible answer.
        """
        ...

    def __lt__(self, other: Guess) -> bool:
        ...

    def __gt__(self, other: Guess) -> bool:
        ...


@dataclass(eq=True, frozen=True)
class MinimaxGuess:
    """Represents a guess using the minimax heuristic."""

    __slots__ = ["word", "is_potential_soln", "number_of_buckets", "size_of_largest_bucket"]

    word: Word
    is_potential_soln: bool
    number_of_buckets: int
    size_of_largest_bucket: int

    def improves_upon(self, other: MinimaxGuess) -> bool:
        """Defines whether the minimax guess improves upon the other.

        Args:
            other (MinimaxGuess): The other minimax guess.

        Returns:
            bool: Whether the guess improves upon the other guess.
        """
        if self.size_of_largest_bucket != other.size_of_largest_bucket:
            return self.size_of_largest_bucket < other.size_of_largest_bucket

        if self.is_potential_soln != other.is_potential_soln:
            return self.is_potential_soln

        if self.number_of_buckets != other.number_of_buckets:
            return self.number_of_buckets > other.number_of_buckets

        return self.word < other.word

    def perfectly_partitions(self) -> bool:
        """Whether a guess partitions the histogram into buckets of size one.

        Returns:
            bool: Returns whether the guess partitions the histogram into bucekts of size one.
        """
        return self.size_of_largest_bucket == 1

    def combine(self, other: MinimaxGuess) -> MinimaxGuess:
        """Combines a guess with a follow-up, deep guess.

        Args:
            other (MinimaxGuess): The follow-up guess.

        Returns:
            MinimaxGuess: Returns the combined guess.
        """
        num_buckets = other.number_of_buckets
        largest_bucket = other.size_of_largest_bucket
        return MinimaxGuess(self.word, self.is_potential_soln, num_buckets, largest_bucket)

    def __rshift__(self, other: MinimaxGuess) -> MinimaxGuess:
        """Syntactic sugar to combine guesses.

        e.g. combined_guess = guess >> deep_guess

        Args:
            other (MinimaxGuess): The follow-up guess.

        Returns:
            MinimaxGuess: Returns the combined guess.
        """
        return self.combine(other)

    def __str__(self) -> str:
        return str(self.word)

    def __repr__(self) -> str:
        flag = "Common" if self.is_potential_soln else "Uncommon"
        return (
            f"Word={self.word} ({flag}), Largest bucket={self.size_of_largest_bucket}, "
            + f"Num. buckets={self.number_of_buckets}"
        )

    def __lt__(self, other: Guess) -> bool:
        if isinstance(other, MinimaxGuess):
            return self.improves_upon(other)

        type1 = type(self).__name__
        type2 = type(other).__name__
        raise TypeError(f"'<' not supported between instances of type '{type1}' and '{type2}'")

    def __gt__(self, other: Guess) -> bool:
        if isinstance(other, MinimaxGuess):
            return other.improves_upon(self)

        type1 = type(self).__name__
        type2 = type(other).__name__
        raise TypeError(f"'<' not supported between instances of type '{type1}' and '{type2}'")

    @staticmethod
    def from_histogram(word: Word, is_potential_soln: bool, histogram: np.ndarray) -> MinimaxGuess:
        num_buckets = np.count_nonzero(histogram)
        size_of_largest_bucket = histogram.max()
        return MinimaxGuess(word, is_potential_soln, num_buckets, size_of_largest_bucket)


@dataclass(eq=True, frozen=True)
class EntropyGuess:
    """Represents a guess using the entropy heuristic."""

    __slots__ = ["word", "is_potential_soln", "entropy", "is_perfect_partition"]

    word: Word
    is_potential_soln: bool
    entropy: float
    is_perfect_partition: bool

    def improves_upon(self, other: EntropyGuess) -> bool:
        """Defines whether the entropy guess improves upon the other.

        Args:
            other (MinimaxGuess): The other entropy guess.

        Returns:
            bool: Whether the guess improves upon the other guess.
        """

        if not isclose(self.entropy, other.entropy, abs_tol=1e-9):
            return self.entropy > other.entropy

        if self.is_potential_soln != other.is_potential_soln:
            return self.is_potential_soln

        return self.word < other.word

    def perfectly_partitions(self) -> bool:
        """Whether a guess partitions the histogram into buckets of size one.

        Returns:
            bool: Returns whether the guess partitions the histogram into bucekts of size one.
        """
        return self.is_perfect_partition

    def __str__(self) -> str:
        return str(self.word)

    def __repr__(self) -> str:
        flag = "Common" if self.is_potential_soln else "Uncommon"
        return f"Word={self.word} ({flag}), Entropy={self.entropy:.4f}"

    def __lt__(self, other: Guess) -> bool:
        if isinstance(other, EntropyGuess):
            return self.improves_upon(other)

        type1 = type(self).__name__
        type2 = type(other).__name__
        raise TypeError(f"'<' not supported between instances of type '{type1}' and '{type2}'")

    def __gt__(self, other: Guess) -> bool:
        if isinstance(other, EntropyGuess):
            return other.improves_upon(self)

        type1 = type(self).__name__
        type2 = type(other).__name__
        raise TypeError(f"'<' not supported between instances of type '{type1}' and '{type2}'")

    def __add__(self, entropy: float) -> EntropyGuess:
        return EntropyGuess(
            self.word, self.is_potential_soln, self.entropy + entropy, self.is_perfect_partition
        )

    @staticmethod
    def from_histogram(word: Word, is_potential_soln: bool, histogram: np.ndarray) -> EntropyGuess:

        counts = histogram[histogram > 0]
        num_buckets = len(counts)
        num_potential_solns = np.sum(counts)
        is_perfect_partition = num_buckets == num_potential_solns

        probabilites = counts / num_potential_solns
        entropy = -probabilites.dot(np.log2(probabilites))
        entropy += 1 / num_potential_solns if is_potential_soln else 0

        return EntropyGuess(word, is_potential_soln, entropy, is_perfect_partition)


@dataclass(eq=True, frozen=True)
class MinimaxSimulGuess:
    """Represents a guess in a simultaneous game using the minimax heuristic."""

    __slots__ = ["word", "is_potential_soln", "pct_left", "min", "sum", "max", "num_buckets"]

    word: Word
    is_potential_soln: bool
    pct_left: float
    min: int
    sum: int
    max: int
    num_buckets: int

    def improves_upon(self, other: MinimaxSimulGuess) -> bool:
        """Defines whether the simultaneous minimax guess improves upon the other.

        Args:
            other (MinimaxGuess): The other guess.

        Returns:
            bool: Whether the guess improves upon the other guess.
        """

        if not isclose(self.pct_left, other.pct_left, abs_tol=1e-9):
            return self.pct_left < other.pct_left

        if self.min != other.min:
            return self.min < other.min

        if self.sum != other.sum:
            return self.sum < other.sum

        if self.max != other.max:
            return self.max < other.max

        if self.is_potential_soln != other.is_potential_soln:
            return self.is_potential_soln

        if self.num_buckets != other.num_buckets:
            return self.num_buckets > other.num_buckets

        return self.word < other.word

    def __str__(self) -> str:
        return str(self.word)

    def __repr__(self) -> str:
        flag = "Common" if self.is_potential_soln else "Uncommon"
        return f"Word={self.word} ({flag}), % Left={self.pct_left:.8f}"

    def __lt__(self, other: Guess) -> bool:
        if isinstance(other, MinimaxSimulGuess):
            return self.improves_upon(other)

        type1 = type(self).__name__
        type2 = type(other).__name__
        raise TypeError(f"'<' not supported between instances of type '{type1}' and '{type2}'")

    def __gt__(self, other: Guess) -> bool:
        if isinstance(other, MinimaxSimulGuess):
            return other.improves_upon(self)

        type1 = type(self).__name__
        type2 = type(other).__name__
        raise TypeError(f"'<' not supported between instances of type '{type1}' and '{type2}'")
