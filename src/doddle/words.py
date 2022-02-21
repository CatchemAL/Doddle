from __future__ import annotations

import json
from bisect import bisect_left
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Sequence

import numpy as np


class Word:

    __slots__ = ["value", "vector"]

    def __init__(self, value: str | Word) -> None:

        if isinstance(value, Word):
            self.value = value.value
            self.vector = value.vector
        else:
            self.value = value.upper()
            self.vector = Word.to_vector(value)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, obj: object) -> bool:
        return isinstance(obj, type(self)) and self.value == obj.value

    def __lt__(self, other: Word) -> bool:
        return self.value < other.value

    def __gt__(self, other: Word) -> bool:
        return self.value > other.value

    def __le__(self, other: Word) -> bool:
        return self.value <= other.value

    def __ge__(self, other: Word) -> bool:
        return self.value >= other.value

    def __len__(self) -> int:
        return len(self.vector)

    def __hash__(self) -> int:
        return hash(self.value)

    def __add__(self, other: str) -> str:
        return self.value + other

    def __iter__(self) -> Iterator[str]:
        return iter(self.value)

    def split(self, separator: str):
        return list(Word(s) for s in self.value.split(separator))

    @staticmethod
    def to_vector(word: str) -> np.ndarray:
        asciis = [ord(c) - 64 for c in word.upper()]
        return np.array(asciis, dtype=np.int8)


class WordSeries:
    def __init__(self, words: Sequence[str] | np.ndarray, index: np.ndarray | None = None) -> None:

        if isinstance(words, np.ndarray) and words.dtype == type(Word):
            self.words = words
        else:
            sorted_words = sorted(words)
            self.words = np.array([Word(w) for w in sorted_words])

        self.index = np.arange(len(sorted_words)) if index is None else index

    @property
    def word_length(self) -> int:
        return 0 if len(self) == 0 else len(self.words[0])

    def contains(self, word: str | Word) -> bool:
        pos = bisect_left(self.words, str(word), key=lambda w: w.value)
        return pos < len(self) and self.words[pos].value == str(word)

    def find_index(self, word: str | Word | np.ndarray) -> int | np.ndarray:
        if isinstance(word, np.ndarray):
            find_func = np.vectorize(self.__find_index)
            return find_func(word)

        return self.__find_index(word)

    def __find_index(self, word: str | Word) -> int:
        pos = bisect_left(self.words, str(word), key=lambda w: w.value)
        if pos < len(self) and self.words[pos] == word:
            return pos
        return -1

    def __getitem__(self, s: slice) -> WordSeries:

        is_slice = isinstance(s, slice)
        is_mask = isinstance(s, np.ndarray) and s.dtype == np.bool8
        is_index = isinstance(s, np.ndarray) and s.dtype == np.int32
        can_index = is_slice or is_mask or is_index

        if can_index:
            sliced_words = self.words[s]
            sliced_index = self.index[s]
            return WordSeries(sliced_words, sliced_index)

        message = (
            "Indexer must be a slice or logical array. "
            + "Use series.loc[5] or series['RAISE'] if you need to index by position or word."
        )

        raise ValueError(message)

    def __len__(self):
        return len(self.index)

    def __iter__(self):
        return iter(self.words)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self):
        if len(self) <= 20:
            lines: list[str] = []
            for i in range(len(self)):
                idx = f"[{self.index[i]}]".ljust(8)
                lines.append(f"{idx}{str(self.words[i])}")
            return "\n".join(lines)
        else:
            top = str(self[:5])
            bottom = str(self[-5:])
            mid = "        ..."
            foot_note = f"Length: {len(self)}"
            row_strings = [top, mid, bottom, foot_note]
            return "\n".join(row_strings)

    @property
    def iloc(self):
        return _WordLoc(self)


class _WordLoc:
    def __init__(self, series: WordSeries) -> None:
        self.series = series

    def __getitem__(self, indexer: int) -> Word:
        if isinstance(indexer, int):
            return self.series.words[indexer]

        raise ValueError("Indexer must be an integer.")


@dataclass
class Dictionary:
    all_words: WordSeries
    common_words: WordSeries

    @property
    def word_length(self) -> int:
        return self.all_words.word_length

    @property
    def words(self) -> tuple[WordSeries, WordSeries]:
        return self.all_words, self.common_words


def load_dictionary(size, extras: Sequence[Word] | None = None) -> Dictionary:

    if size == 5:
        # Use the official Wordle list for the real game
        all_words = _load_from_file("dictionary-full-official.json", size)
        common_words = _load_from_file("dictionary-answers-official.json", size)
    else:
        all_words = _load_from_file("dictionary-full.json", size)
        common_words = _load_from_file("dictionary-answers.json", size)

    # Add any extra words in case they're missing from the official dictionary
    # Better to solve an unofficial word than bomb out later.
    extras_str = [str(word) for word in extras if word] if extras else []
    common_words.update(extras_str)
    all_words.update(common_words)

    common_series = WordSeries(common_words)
    all_series = WordSeries(all_words)
    return Dictionary(all_series, common_series)


def _load_from_file(file_name: str, size: int) -> set[str]:

    SUB_FOLDER = "dictionaries"
    path = Path(__file__).parent.absolute()

    with open(path / SUB_FOLDER / file_name) as file:
        word_list = json.load(file)

    return {word.upper() for word in word_list if len(word) == size}
