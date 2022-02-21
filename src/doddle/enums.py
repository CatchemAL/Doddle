from __future__ import annotations

from enum import Enum


class SolverType(Enum):
    MINIMAX = "MINIMAX"
    ENTROPY = "ENTROPY"

    @staticmethod
    def from_str(value: str) -> SolverType:
        if value.upper() == "MINIMAX":
            return SolverType.MINIMAX
        if value.upper() == "ENTROPY":
            return SolverType.ENTROPY
        supported_types = ", ".join(list(SolverType))
        message = f"{value} not a supported solver type. Supported types are {supported_types}."
        raise ValueError(message)
