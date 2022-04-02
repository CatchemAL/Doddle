from unittest.mock import MagicMock, patch

import pytest

from doddle import factory
from doddle.benchmarking import Benchmarker, SimulBenchmarker
from doddle.engine import Engine, SimulEngine
from doddle.enums import SolverType
from doddle.exceptions import SolverNotSupportedError
from doddle.factory import (
    create_benchmarker,
    create_engine,
    create_models,
    create_simul_benchmarker,
    create_simul_engine,
)
from doddle.solver import DeepEntropySolver, DeepMinimaxSolver, EntropySolver, MinimaxSolver
from tests.fake_dictionary import load_test_dictionary


class TestFactory:
    @patch.object(factory, "load_dictionary")
    def test_create_engine(self, patch_load_dictionary: MagicMock) -> None:
        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()

        # Act
        engine = create_engine(5)

        # Assert
        assert engine is not None
        assert isinstance(engine, Engine)

    @patch.object(factory, "load_dictionary")
    def test_create_simul_engine(self, patch_load_dictionary: MagicMock) -> None:
        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()

        # Act
        engine = create_simul_engine(5)

        # Assert
        assert engine is not None
        assert isinstance(engine, SimulEngine)

    @patch.object(factory, "load_dictionary")
    def test_create_benchmarker(self, patch_load_dictionary: MagicMock) -> None:
        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()

        # Act
        benchmarker = create_benchmarker(5)

        # Assert
        assert benchmarker is not None
        assert isinstance(benchmarker, Benchmarker)

    @patch.object(factory, "load_dictionary")
    def test_create_simul_benchmarker(self, patch_load_dictionary: MagicMock) -> None:
        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()

        # Act
        benchmarker = create_simul_benchmarker(5)

        # Assert
        assert benchmarker is not None
        assert isinstance(benchmarker, SimulBenchmarker)

    @patch.object(factory, "load_dictionary")
    def test_create_models(self, patch_load_dictionary: MagicMock) -> None:
        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()

        # Act
        _, _, _, solver1m, _ = create_models(5, solver_type=SolverType.MINIMAX, depth=1)
        _, _, _, solver2m, _ = create_models(5, solver_type=SolverType.MINIMAX, depth=2)
        _, _, _, solver1e, _ = create_models(5, solver_type=SolverType.ENTROPY, depth=1)
        _, _, _, solver2e, _ = create_models(5, solver_type=SolverType.ENTROPY, depth=2)

        # Assert
        assert isinstance(solver1m, MinimaxSolver)
        assert isinstance(solver2m, DeepMinimaxSolver)
        assert isinstance(solver1e, EntropySolver)
        assert isinstance(solver2e, DeepEntropySolver)

    @patch.object(factory, "load_dictionary")
    def test_create_models_with_unrecognised_enum_raises(self, patch_load_dictionary: MagicMock) -> None:
        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()
        solver_type = "UnknownSolverType"

        # Act
        with pytest.raises(SolverNotSupportedError):
            create_models(5, solver_type=solver_type, depth=1)
