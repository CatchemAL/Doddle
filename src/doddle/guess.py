from __future__ import annotations

from dataclasses import dataclass
from math import isclose
from typing import Protocol

from .words import Word


class Guess(Protocol):
    @property
    def word(self) -> Word:
        ...

    @property
    def is_common_word(self) -> bool:
        ...


@dataclass(eq=True, frozen=True)
class MinimaxGuess:

    __slots__ = ["word", "is_common_word", "number_of_buckets", "size_of_largest_bucket"]

    word: Word
    is_common_word: bool
    number_of_buckets: int
    size_of_largest_bucket: int

    def improves_upon(self, other: MinimaxGuess) -> bool:

        if self.size_of_largest_bucket != other.size_of_largest_bucket:
            return self.size_of_largest_bucket < other.size_of_largest_bucket

        if self.is_common_word != other.is_common_word:
            return self.is_common_word

        if self.number_of_buckets != other.number_of_buckets:
            return self.number_of_buckets > other.number_of_buckets

        return self.word < other.word

    def __str__(self) -> str:
        return str(self.word)

    def __repr__(self) -> str:
        flag = "Common" if self.is_common_word else "Uncommon"
        return (
            f"Word={self.word} ({flag}), Largest bucket={self.size_of_largest_bucket}, "
            + f"Num. buckets={self.number_of_buckets}"
        )

    def __lt__(self, other: MinimaxGuess):
        return self.improves_upon(other)

    def __gt__(self, other: MinimaxGuess):
        return other.improves_upon(self)


@dataclass(eq=True, frozen=True)
class EntropyGuess:

    __slots__ = ["word", "is_common_word", "entropy"]

    word: Word
    is_common_word: bool
    entropy: float

    def improves_upon(self, other: EntropyGuess) -> bool:

        if not isclose(self.entropy, other.entropy, abs_tol=1e-9):
            return self.entropy > other.entropy

        if self.is_common_word != other.is_common_word:
            return self.is_common_word

        return self.word < other.word

    def __str__(self) -> str:
        return str(self.word)

    def __repr__(self) -> str:
        flag = "Common" if self.is_common_word else "Uncommon"
        return f"Word={self.word} ({flag}), Entropy={self.entropy}"

    def __lt__(self, other: EntropyGuess):
        return self.improves_upon(other)

    def __gt__(self, other: EntropyGuess):
        return other.improves_upon(self)

    def __add__(self, entropy: float) -> EntropyGuess:
        return EntropyGuess(self.word, self.is_common_word, self.entropy + entropy)


@dataclass(eq=True, frozen=True)
class MinimaxSimulGuess:

    word: Word
    is_common_word: bool
    pct_left: float
    min: int
    sum: int
    max: int
    num_buckets: int

    def improves_upon(self, other: MinimaxSimulGuess) -> bool:

        if not isclose(self.pct_left, other.pct_left, abs_tol=1e-9):
            return self.pct_left < other.pct_left

        if self.min != other.min:
            return self.min < other.min

        if self.sum != other.sum:
            return self.sum < other.sum

        if self.max != other.max:
            return self.max < other.max

        if self.is_common_word != other.is_common_word:
            return self.is_common_word

        if self.num_buckets != other.num_buckets:
            return self.num_buckets > other.num_buckets

        return self.word < other.word

    def __str__(self) -> str:
        return str(self.word)

    def __repr__(self) -> str:
        flag = "Common" if self.is_common_word else "Uncommon"
        return f"Word={self.word} ({flag}), % Left={self.pct_left:.8f}"

    def __lt__(self, other: MinimaxSimulGuess):
        return self.improves_upon(other)

    def __gt__(self, other: MinimaxSimulGuess):
        return other.improves_upon(self)
