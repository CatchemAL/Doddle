from __future__ import annotations

import json
from bisect import bisect_left
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence, cast

import numpy as np


class Word:
    """Represents a word within the game.

    Internally stores an integer vector representation of the word
    for optimised scoring and comparisons.

    Enforces capitalisation of the word.
    """

    __slots__ = ["value", "vector"]

    def __init__(self, word: str | Word) -> None:
        """Initisalises a new instance of a Word

        Args:
            word (str | Word): The word
        """
        self.value = str(word).upper()
        self.vector = Word.to_vector(self.value)

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

    def split(self, sep: str) -> list[Word]:
        """Returns a list of Words using sep as the delimiter

        Args:
            sep (str): The separator

        Returns:
            list[Word]: The separated list of words
        """
        return list(Word(s) for s in self.value.split(sep))

    @staticmethod
    def to_vector(word: str) -> np.ndarray:
        """Converts a string into an integer vector representation.

        Args:
            word (str): The string word to convert.

        Returns:
            np.ndarray: Returns the resultant integer vector.
        """
        asciis = [ord(c) - ord("A") for c in word.upper()]
        return np.array(asciis, dtype=np.int8)


class WordSeries:
    def __init__(self, words: Iterable[str] | np.ndarray, index: np.ndarray | None = None) -> None:
        """Initialises a new instance of the WordSeries object.

        Args:
          words (Iterable[str] | np.ndarray):
            The words in the series.

          index (np.ndarray | None, optional):
            The numerical index associated with each word. Defaults to None.
        """

        if isinstance(words, np.ndarray) and words.dtype == type(Word):
            self.words = words
        else:
            sorted_words = sorted(words)
            self.words = np.array([Word(w) for w in sorted_words])

        self.index = np.arange(len(sorted_words)) if index is None else index

    @property
    def word_length(self) -> int:
        """The length of each word in the series.

        Returns:
            int: Returns the length of each word in the series.
        """
        return 0 if len(self) == 0 else len(self.words[0])

    def __contains__(self, value: str | Word) -> bool:
        """Whether the series contains the word

        Args:
            value (str | Word): The word.

        Returns:
            bool: Returns True if the word is in the series.
        """
        return self.__find_index(value) >= 0

    def find_index(self, word: str | Word | np.ndarray) -> int | np.ndarray:  # TODO @overload
        """Finds the numerical index associated with a Word in the series.

        Args:
            word (str | Word | np.ndarray): The word or vector of words.

        Returns:
            int | np.ndarray: The index or array of indices.
        """
        if isinstance(word, np.ndarray):
            find_func = np.vectorize(self.__find_index)
            return find_func(word)

        return self.__find_index(word)

    def __find_index(self, value: str | Word) -> int:
        word = Word(value)
        words = cast(Sequence[Word], self.words)
        pos = bisect_left(words, word)
        if pos < len(self) and words[pos] == word:
            return pos
        return -1

    def __getitem__(self, s: slice | np.ndarray) -> WordSeries:

        is_slice = isinstance(s, slice)
        is_mask = isinstance(s, np.ndarray) and s.dtype == np.bool8
        is_index = isinstance(s, np.ndarray) and s.dtype == np.int_
        can_index = is_slice or is_mask or is_index

        if can_index:
            sliced_words = self.words[s]
            sliced_index = self.index[s]
            return WordSeries(sliced_words, sliced_index)

        message = (
            "Indexer must be a slice or logical array. "
            + "Use series.iloc[5] if you need to index by position."
        )

        raise ValueError(message)

    def __len__(self) -> int:
        return len(self.index)

    def __iter__(self):
        return iter(self.words)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
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
    def iloc(self) -> _iLocIndexer:
        return _iLocIndexer(self)


class _iLocIndexer:
    def __init__(self, series: WordSeries) -> None:
        self.series = series

    def __getitem__(self, indexer: int) -> Word:
        if isinstance(indexer, int):
            return self.series.words[indexer]

        raise ValueError("Indexer must be an integer.")


@dataclass
class Dictionary:
    """The collection of all words (of a given word length).

    The dictionary holds two members:

    1) A list of all words that could be accepted as a guess

    2) A list of common words that might possibly be a solution. This
       is a subset as uncommon words, plurals etc. are not valid
       solutions.
    """

    all_words: WordSeries
    common_words: WordSeries

    @property
    def word_length(self) -> int:
        """Gets the word length

        Returns:
            int: Returns the word length
        """
        return self.all_words.word_length

    @property
    def words(self) -> tuple[WordSeries, WordSeries]:
        """The tuple of all words and common words.

        Returns:
          tuple[WordSeries, WordSeries]:
            Returns a tuple of all_words and common words.
        """
        return self.all_words, self.common_words


def load_dictionary(size, extras: Sequence[Word] | None = None) -> Dictionary:
    """Loads a dictionary of words of specified word length, size.

    Args:
      size (_type_):
        The length of each word in the dictionary.

      extras (Sequence[Word] | None, optional):
        Any additional words to include in the dictionary. Defaults to None.

    Returns:
        Dictionary: Returns the dictionary.
    """

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
