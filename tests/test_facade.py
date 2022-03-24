from unittest.mock import MagicMock, patch

import pytest

from doddle import Doddle, factory

from .fake_dictionary import load_test_dictionary


class TestDoddle:
    @patch.object(factory, "load_dictionary")
    def test_doddle_with_trivial_solve(self, patch_load_dictionary: MagicMock) -> None:
        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()

        sut = Doddle()

        # Act
        scoreboard = sut(answer="SNAKE", guess=["RAISE", "SNACK", "BRAKE"])

        # Assert
        assert len(scoreboard.rows) == 4

    @patch.object(factory, "load_dictionary")
    def test_doddle_with_trivial_simul_solve(self, patch_load_dictionary: MagicMock) -> None:
        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()

        sut = Doddle()

        # Act
        scoreboard = sut(answer=["SNAKE", "FLACK"], guess=["FLAME", "SNACK", "BRAKE"])
        scoreboards = scoreboard.many()

        # Assert
        assert len(scoreboards) == 2
        assert len(scoreboards[0]) == 4
        assert len(scoreboards[1]) == 5

    @patch.object(factory, "load_dictionary")
    def test_doddle_with_null_answer(self, patch_load_dictionary: MagicMock) -> None:
        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()

        sut = Doddle(size=5, solver_type="MINIMAX")

        # Act + Assert
        with pytest.raises(TypeError):
            sut(answer=None)

    @patch.object(factory, "load_dictionary")
    def test_doddle_with_incorrect_answer_size(self, patch_load_dictionary: MagicMock) -> None:
        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()

        sut = Doddle(size=5, solver_type="ENTROPY")

        # Act + Assert
        with pytest.raises(ValueError):
            sut(answer="SNAKES", guess=["RAISE", "SNACK", "BRAKE"])

    @patch.object(factory, "load_dictionary")
    def test_doddle_with_incorrect_guess_size(self, patch_load_dictionary: MagicMock) -> None:
        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()

        sut = Doddle(size=5, solver_type="ENTROPY")

        # Act + Assert
        with pytest.raises(ValueError):
            sut(answer="LIGHT", guess=["RAISED", "SNACKS", "BRAKES"])

    @patch.object(factory, "load_dictionary")
    def test_doddle_with_unknown_soln_word(self, patch_load_dictionary: MagicMock) -> None:
        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()

        sut = Doddle(size=5, solver_type="ENTROPY")

        # Act + Assert
        with pytest.raises(ValueError):
            sut(answer="QXZWJ", guess=["RAISE", "SNACK", "BRAKE"])

    @patch.object(factory, "load_dictionary")
    def test_doddle_with_unknown_guess_word(self, patch_load_dictionary: MagicMock) -> None:
        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()

        sut = Doddle(size=5, solver_type="ENTROPY")

        # Act + Assert
        with pytest.raises(ValueError):
            sut(answer="TOWER", guess=["RAISE", "QXZWJ", "BRAKE"])
