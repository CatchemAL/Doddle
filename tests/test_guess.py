from doddle.guess import EntropyGuess, MinimaxGuess
from doddle.words import Word


class TestMinimaxGuess:
    def test_minimax_guess_where_largest_bucket_differs(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        guess1 = MinimaxGuess(word1, True, 4, 20)
        guess2 = MinimaxGuess(word2, True, 4, 25)

        # Act
        is_better = guess1 < guess2
        is_worse = guess1 > guess2

        # Assert
        assert is_better
        assert not is_worse

    def test_minimax_guess_where_common_differs(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        guess1 = MinimaxGuess(word1, True, 4, 20)
        guess2 = MinimaxGuess(word2, False, 4, 20)

        # Act
        is_better = guess1 < guess2
        is_worse = guess1 > guess2

        # Assert
        assert is_better
        assert not is_worse

    def test_minimax_guess_where_number_of_buckets_differ(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        guess1 = MinimaxGuess(word1, True, 5, 20)
        guess2 = MinimaxGuess(word2, True, 4, 20)

        # Act
        is_better = guess1 < guess2
        is_worse = guess1 > guess2

        # Assert
        assert is_better
        assert not is_worse

    def test_minimax_guess_where_all_same_sorts_alphabetically(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        guess1 = MinimaxGuess(word1, False, 5, 20)
        guess2 = MinimaxGuess(word2, False, 5, 20)

        # Act
        is_better = guess1 < guess2
        is_worse = guess1 > guess2

        # Assert
        assert not is_better
        assert is_worse


class TestEntropyGuess:
    def test_entropy_guess_where_expected_shannon_entropy_differs(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        guess1 = EntropyGuess(word1, True, 5.3)
        guess2 = EntropyGuess(word2, True, 4.8)

        # Act
        is_better = guess1 < guess2
        is_worse = guess1 > guess2

        # Assert
        assert is_better
        assert not is_worse

    def test_entropy_guess_where_common_differs(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        guess1 = MinimaxGuess(word1, True, 4, 5.3)
        guess2 = MinimaxGuess(word2, False, 4, 5.3)

        # Act
        is_better = guess1 < guess2
        is_worse = guess1 > guess2

        # Assert
        assert is_better
        assert not is_worse

    def test_entropy_guess_where_all_same_sorts_alphabetically(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        guess1 = MinimaxGuess(word1, False, 5, 5.3)
        guess2 = MinimaxGuess(word2, False, 5, 5.3)

        # Act
        is_better = guess1 < guess2
        is_worse = guess1 > guess2

        # Assert
        assert not is_better
        assert is_worse
