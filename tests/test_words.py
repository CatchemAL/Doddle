from doddle.words import Word


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
        assert joined_chars == "SNAKE"

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
