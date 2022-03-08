import pytest
from doddle.enums import SolverType

class TestSolverType:

    def test_parse_minimax(self) -> None:
        # Arrange
        value = "minimax"

        # Act
        solver_type = SolverType.from_str(value)

        # Assert
        assert solver_type == SolverType.MINIMAX

    def test_parse_entropy(self) -> None:
        # Arrange
        value = "entropy"

        # Act
        solver_type = SolverType.from_str(value)

        # Assert
        assert solver_type == SolverType.ENTROPY

    def test_raises_value_error_if_unknown(self) -> None:
        # Arrange
        value = "typo"

        # Act + Assert
        with pytest.raises(ValueError):
            SolverType.from_str(value)