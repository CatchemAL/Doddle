from unittest.mock import MagicMock, patch

from doddle.scoring import from_ternary
from doddle.views import HideView, InputMixin, SolveView
from doddle.words import Word


class TestSolveView:
    @patch.object(InputMixin, "get_input")
    def test_get_user_score_with_score_word_pair(self, patch_get_input: MagicMock) -> None:
        # Arrange
        patch_get_input.side_effect = ["INVALID_WORD", "INVALID_SCORE=1", "POWER=20100"]
        expected_score = from_ternary("20100")
        expected_word = Word("POWER")
        guess = Word("SHARP")

        sut = SolveView(5)

        # Act
        score, word = sut.get_user_score(guess)

        # Assert
        assert score == expected_score
        assert word == expected_word

    @patch.object(InputMixin, "get_input")
    def test_get_user_score_with_score(self, patch_get_input: MagicMock) -> None:
        # Arrange
        patch_get_input.side_effect = ["INVALID_WORD", "INVALID_SCORE=1", "20100"]
        expected_score = from_ternary("20100")
        guess = Word("SHARP")

        sut = SolveView(5)

        # Act
        score, word = sut.get_user_score(guess)

        # Assert
        assert score == expected_score
        assert word == guess


class TestHideView:
    @patch.object(InputMixin, "get_input")
    def test_get_user_score_with_score_word_pair(self, patch_get_input: MagicMock) -> None:
        # Arrange
        patch_get_input.side_effect = ["INVALID_WORD", "12345", "POWER"]
        expected_word = Word("POWER")

        sut = HideView(5)

        # Act
        word = sut.get_user_guess()

        # Assert
        assert word == expected_word
