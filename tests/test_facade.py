import pytest

from doddle import Doddle


class TestDoddle:
    def test_doddle_with_trivial_solve(self) -> None:
        # Arrange
        sut = Doddle()

        # Act
        scoreboard = sut(answer="SNAKE", guess=["RAISE", "SNACK", "BRAKE"])

        # Assert
        assert len(scoreboard.rows) == 4

    def test_doddle_with_trivial_simul_solve(self) -> None:
        # Arrange
        sut = Doddle()

        # Act
        scoreboard = sut(answer=["SNAKE", "FLACK"], guess=["FLAME", "SNACK", "BRAKE"])
        scoreboards = scoreboard.many()

        # Assert
        assert len(scoreboards) == 2
        assert len(scoreboards[0]) == 4
        assert len(scoreboards[1]) == 5

    def test_doddle_with_null_answer_size(self) -> None:
        # Arrange
        sut = Doddle(size=5, solver_type="MINIMAX")

        # Act + Assert
        with pytest.raises(TypeError):
            sut(answer=None)

    def test_doddle_with_incorrect_answer_size(self) -> None:
        # Arrange
        sut = Doddle(size=6, solver_type="ENTROPY")

        # Act + Assert
        with pytest.raises(ValueError):
            sut(answer="SNAKE", guess=["RAISE", "SNACK", "BRAKE"])

    def test_doddle_with_incorrect_guess_size(self) -> None:
        # Arrange
        sut = Doddle(size=6, solver_type="ENTROPY")

        # Act + Assert
        with pytest.raises(ValueError):
            sut(answer="FLIGHT", guess=["RAISE", "SNACK", "BRAKE"])

    def test_doddle_with_unknown_soln_word(self) -> None:
        # Arrange
        sut = Doddle(size=5, solver_type="ENTROPY")

        # Act + Assert
        with pytest.raises(ValueError):
            sut(answer="QXZWJ", guess=["RAISE", "SNACK", "BRAKE"])

    def test_doddle_with_unknown_guess_word(self) -> None:
        # Arrange
        sut = Doddle(size=5, solver_type="ENTROPY")

        # Act + Assert
        with pytest.raises(ValueError):
            sut(answer="TOWER", guess=["RAISE", "QXZWJ", "BRAKE"])
