from unittest.mock import MagicMock, patch

from doddle import cli
from doddle.enums import SolverType
from doddle.words import Word


class TestMain:
    @patch.object(cli, "create_engine")
    def test_cli_with_single_run(self, patch_create_engine: MagicMock) -> None:
        # Arrange
        run_args = ["run", "--answer=FLAME"]

        expected_word = Word("FLAME")
        expected_size = 5
        expected_solver_type = SolverType.MINIMAX
        expected_depth = 1
        expected_extras = [expected_word]

        mock_engine = MagicMock()
        mock_engine.run = MagicMock()
        patch_create_engine.return_value = mock_engine

        # Act
        cli.parse_args(run_args)

        # Assert
        patch_create_engine.assert_called_once_with(
            expected_size, solver_type=expected_solver_type, depth=expected_depth, extras=expected_extras
        )

        mock_engine.run.assert_called_once_with(expected_word, [])

    @patch.object(cli, "create_simul_engine")
    def test_cli_with_simul_run(self, patch_create_simul_engine: MagicMock) -> None:
        # Arrange
        run_args = [
            "run",
            "--answer=FLAME,BLAME,SHAME,FRAME",
            "--guess=START",
            "--depth=2",
            "--solver=entropy",
        ]

        expected_solutions = [Word("FLAME"), Word("BLAME"), Word("SHAME"), Word("FRAME")]
        expected_guesses = [Word("START")]
        expected_size = 5
        expected_solver_type = SolverType.ENTROPY
        expected_depth = 2
        expected_extras = expected_solutions + expected_guesses

        mock_engine = MagicMock()
        mock_engine.run = MagicMock()
        patch_create_simul_engine.return_value = mock_engine

        # Act
        cli.parse_args(run_args)

        # Assert
        patch_create_simul_engine.assert_called_once_with(
            expected_size, solver_type=expected_solver_type, depth=expected_depth, extras=expected_extras
        )

        mock_engine.run.assert_called_once_with(expected_solutions, expected_guesses)

    @patch.object(cli, "create_benchmarker")
    def test_cli_with_single_benchmark(self, patch_create_benchmarker: MagicMock) -> None:
        # Arrange
        run_args = ["benchmark", "--guess=RAISE,LOFTY", "--solver=minimax"]

        expected_guesses = [Word("RAISE"), Word("LOFTY")]
        expected_size = 5
        expected_solver_type = SolverType.MINIMAX
        expected_depth = 1
        expected_extras = expected_guesses

        mock_benchmarker = MagicMock()
        mock_benchmarker.run_benchmark = MagicMock()
        patch_create_benchmarker.return_value = mock_benchmarker

        # Act
        cli.parse_args(run_args)

        # Assert
        patch_create_benchmarker.assert_called_once_with(
            expected_size, solver_type=expected_solver_type, depth=expected_depth, extras=expected_extras
        )

        mock_benchmarker.run_benchmark.assert_called_once_with(expected_guesses)

    @patch.object(cli, "create_simul_benchmarker")
    def test_cli_with_simul_benchmark(self, patch_create_simul_benchmarker: MagicMock) -> None:
        # Arrange
        run_args = [
            "benchmark",
            "--simul=4",
            "--guess=START",
            "--solver=entropy",
            "--depth=3",
        ]

        expected_guesses = [Word("START")]
        expected_size = 5
        expected_solver_type = SolverType.ENTROPY
        expected_depth = 3
        expected_simul = 4
        expected_extras = expected_guesses

        mock_simul_benchmarker = MagicMock()
        mock_simul_benchmarker.run_benchmark = MagicMock()
        patch_create_simul_benchmarker.return_value = mock_simul_benchmarker

        # Act
        cli.parse_args(run_args)

        # Assert
        patch_create_simul_benchmarker.assert_called_once_with(
            expected_size, solver_type=expected_solver_type, depth=expected_depth, extras=expected_extras
        )

        mock_simul_benchmarker.run_benchmark.assert_called_once_with(expected_guesses, expected_simul)
