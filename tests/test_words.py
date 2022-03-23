import numpy as np
import pytest

from doddle.words import Word, WordSeries


class TestWords:
    def test_word_compares_correctly(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        word3 = Word("snake")
        word4 = Word(word1)

        # Act + Assert
        assert word1 > word2
        assert word1 >= word2
        assert word1 == word3
        assert word2 < word3
        assert word2 <= word3
        assert word4 == word1
        assert len(word3) == 5

    def test_split_word(self) -> None:
        # Arrange
        word1 = Word("SNAKE,RAISE")
        expected0 = Word("snake")
        expected1 = Word("raise")

        # Act
        words = word1.split(",")

        # Assert
        assert len(words) == 2
        assert words[0] == expected0
        assert words[1] == expected1

    def test_word_iteration(self) -> None:
        # Arrange
        word = Word("snake")

        # Act
        chars = list(word)
        joined_chars = "".join(chars)

        # Assert
        assert joined_chars == repr(word)

    def test_word_hashing(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        word3 = Word("snake")
        word4 = Word(word1)

        # Act
        words = {word1, word2, word3, word4}

        # Assert
        assert len(words) == 2
        assert word1 in words
        assert word2 in words
        assert word3 in words
        assert word4 in words


class TestWordSeries:
    def test_wordseries_regular_index_slice(self) -> None:
        # Arrange
        alphabet = [chr(i + ord("A")) for i in np.arange(0, 26)]
        series = WordSeries(alphabet)
        expected_index = np.array([2, 3, 4])
        expected_words = np.array([Word("C"), Word("D"), Word("E")])

        # Act
        sliced = series[2:5]

        # Assert
        assert np.all(sliced.index == expected_index)
        assert np.all(sliced.words == expected_words)

    def test_wordseries_irregular_index_slice(self) -> None:
        # Arrange
        alphabet = [chr(i + ord("A")) for i in np.arange(0, 26)]
        series = WordSeries(alphabet)[np.arange(2, 26, 3)]
        expected_index = np.array([8, 11, 14])
        expected_words = np.array([Word(c) for c in list("ILO")])

        # Act
        sliced = series[2:5]

        # Assert
        assert np.all(sliced.index == expected_index)
        assert np.all(sliced.words == expected_words)

    def test_wordseries_find_index(self) -> None:
        # Arrange
        alphabet = [chr(i + ord("A")) for i in np.arange(0, 26)]
        series = WordSeries(alphabet)

        # Act
        index1 = series.find_index("C")
        index2 = series.find_index("N/A")
        index3 = series.find_index(np.array(["C", "E"]))

        # Assert
        assert index1 == +2
        assert index2 == -1
        assert np.all(index3 == np.array([2, 4]))

    def test_wordseries_contains(self) -> None:
        # Arrange
        series = WordSeries(["XYZ", "ABC", "PQR"])

        # Act
        contains1 = "XYZ" in series
        contains2 = "abc" in series
        contains3 = "PQR" in series
        contains3 = "PQR" in series
        contains4 = "nah" in series
        contains1b = Word("XYZ") in series
        contains2b = Word("abc") in series
        contains3b = Word("PQR") in series
        contains4b = Word("nah") in series

        # Assert
        assert contains1
        assert contains2
        assert contains3
        assert not contains4
        assert contains1b
        assert contains2b
        assert contains3b
        assert not contains4b

    def test_wordseries_iloc(self) -> None:
        # Arrange
        series = WordSeries(["XYZ", "ABC", "PQR"])
        expected = Word("PQR")

        # Act
        actual = series.iloc[1]

        # Assert
        assert actual == expected

    def test_wordseries_repr(self) -> None:
        # Arrange
        series = WordSeries(["XYZ", "ABC", "PQR"])
        expected = "[0]     ABC\n[1]     PQR\n[2]     XYZ"

        alphabet_long = [chr(i + ord("A")) for i in np.arange(0, 26)] * 5
        series_long = WordSeries(alphabet_long)

        # Act
        actual_repr = repr(series)
        actual_str = str(series)

        # Assert
        assert actual_repr == expected
        assert actual_str == actual_repr
        assert repr(series_long) == str(series_long)

    def test_wordseries_iloc_raises_if_not_integer(self) -> None:
        # Arrange
        series = WordSeries(["XYZ", "ABC", "PQR"])

        # Act + Assert
        with pytest.raises(ValueError):
            series.iloc["ABC"]

    def test_wordseries_indexing_raises(self) -> None:
        # Arrange
        series = WordSeries(["XYZ", "ABC", "PQR"])

        # Act + Assert
        with pytest.raises(ValueError):
            series.iloc[["ABC", "XYZ"]]
