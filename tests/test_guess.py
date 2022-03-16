from doddle.guess import EntropyGuess, MinimaxGuess, MinimaxSimulGuess
from doddle.words import Word
import pytest


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

    def test_minimax_guess_against_different_guess_raises(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        guess1 = MinimaxGuess(word1, False, 5, 20)
        guess2 = EntropyGuess(word2, False, 5)

        # Act + Assert
        with pytest.raises(TypeError):
            guess1 < guess2

        with pytest.raises(TypeError):
            guess1 > guess2

    def test_minimax_guess_representation(self) -> None:
        # Arrange
        word1 = Word("beard")
        guess1 = MinimaxGuess(word1, True, 4, 20)

        # Act
        string = str(guess1)
        str_repr = repr(guess1)

        # Assert
        assert string == "BEARD"
        assert str_repr == "Word=BEARD (Common), Largest bucket=20, Num. buckets=4"


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
        assert str(word1) == "SNAKE"
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

    def test_entropy_guess_where_all_same_sorts_alphabetically(self) -> None:
        # Arrange
        word = Word("SNAKE")
        guess = EntropyGuess(word, False, 5)
        extra_entropy = 3
        expected = 8

        # Act
        deep_guess = guess + extra_entropy

        # Assert
        assert deep_guess.word == guess.word
        assert deep_guess.is_common_word == guess.is_common_word
        assert deep_guess.entropy == expected

    def test_entropy_guess_against_different_guess_raises(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        guess1 = MinimaxGuess(word1, False, 5, 20)
        guess2 = EntropyGuess(word2, False, 5)

        # Act + Assert
        with pytest.raises(TypeError):
            guess2 < guess1

        with pytest.raises(TypeError):
            guess2 > guess1

    def test_entropy_guess_representation(self) -> None:
        # Arrange
        word1 = Word("snake")
        guess1 = EntropyGuess(word1, True, 4.654321)

        # Act
        string = str(guess1)
        str_repr = repr(guess1)

        # Assert
        assert string == "SNAKE"
        assert str_repr == "Word=SNAKE (Common), Entropy=4.6543"


class TestMinimaxSimulGuess:
    def test_minimax_simul_guess_where_joint_probability_differs(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        guess1 = MinimaxSimulGuess(word1, True, 0.01, 4, 25, 7, 20)
        guess2 = MinimaxSimulGuess(word2, True, 0.02, 4, 25, 7, 20)

        # Act
        is_better = guess1 < guess2
        is_worse = guess1 > guess2

        # Assert
        assert is_better
        assert not is_worse

    def test_minimax_guess_where_min_differs(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        guess1 = MinimaxSimulGuess(word1, False, 0.01, 3, 25, 7, 20)
        guess2 = MinimaxSimulGuess(word2, True, 0.01, 4, 25, 7, 20)

        # Act
        is_better = guess1 < guess2
        is_worse = guess1 > guess2

        # Assert
        assert is_better
        assert not is_worse

    def test_minimax_guess_where_sum_differs(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        guess1 = MinimaxSimulGuess(word1, False, 0.01, 4, 24, 7, 20)
        guess2 = MinimaxSimulGuess(word2, True, 0.01, 4, 25, 7, 20)

        # Act
        is_better = guess1 < guess2
        is_worse = guess1 > guess2

        # Assert
        assert is_better
        assert not is_worse

    def test_minimax_guess_where_max_differs(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        guess1 = MinimaxSimulGuess(word1, False, 0.01, 4, 25, 6, 20)
        guess2 = MinimaxSimulGuess(word2, True, 0.01, 4, 25, 7, 20)

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
        guess1 = MinimaxSimulGuess(word1, True, 0.01, 4, 25, 7, 20)
        guess2 = MinimaxSimulGuess(word2, False, 0.01, 4, 25, 7, 20)

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
        guess1 = MinimaxSimulGuess(word1, True, 0.01, 4, 25, 7, 21)
        guess2 = MinimaxSimulGuess(word2, True, 0.01, 4, 25, 7, 20)

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
        guess1 = MinimaxSimulGuess(word1, True, 0.01, 4, 25, 7, 21)
        guess2 = MinimaxSimulGuess(word2, True, 0.01, 4, 25, 7, 21)

        # Act
        is_better = guess1 < guess2
        is_worse = guess1 > guess2

        # Assert
        assert not is_better
        assert is_worse

    def test_minimax_guess_against_different_guess_raises(self) -> None:
        # Arrange
        word1 = Word("SNAKE")
        word2 = Word("SHARK")
        guess1 = MinimaxSimulGuess(word1, True, 0.01, 4, 25, 7, 20)
        guess2 = EntropyGuess(word2, False, 5)

        # Act + Assert
        with pytest.raises(TypeError):
            guess1 < guess2

        with pytest.raises(TypeError):
            guess1 > guess2

    def test_minimax_guess_representation(self) -> None:
        # Arrange
        word1 = Word("beard")
        guess1 = MinimaxSimulGuess(word1, True, 0.01, 4, 25, 7, 20)

        # Act
        string = str(guess1)
        str_repr = repr(guess1)

        # Assert
        assert string == "BEARD"
        assert str_repr == r"Word=BEARD (Common), % Left=0.01000000"
