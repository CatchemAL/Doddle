from __future__ import annotations

from enum import Enum


class SolverType(Enum):
    """Enum representing the supported solver types."""

    MINIMAX = "MINIMAX"
    ENTROPY = "ENTROPY"

    @staticmethod
    def from_str(value: str) -> SolverType:
        """Converts a string to its enum representation.

        Args:
            value (str): The string.

        Raises:
            ValueError: If the string is not recognised.

        Returns:
            SolverType: The enum
        """
        if value.upper() == "MINIMAX":
            return SolverType.MINIMAX
        if value.upper() == "ENTROPY":
            return SolverType.ENTROPY
        supported_types = ", ".join(list(SolverType))
        message = f"{value} not a supported solver type. Supported types are {supported_types}."
        raise ValueError(message)
