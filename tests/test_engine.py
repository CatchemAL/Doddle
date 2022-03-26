from concurrent.futures import ProcessPoolExecutor
from typing import Iterable
from unittest.mock import ANY, MagicMock, patch

import pytest

from doddle import factory
from doddle.engine import Engine, SimulEngine
from doddle.exceptions import FailedToFindASolutionError
from doddle.game import Game, SimultaneousGame
from doddle.guess import EntropyGuess, MinimaxGuess
from doddle.histogram import HistogramBuilder
from doddle.scoring import Scorer
from doddle.simul_solver import MinimaxSimulSolver
from doddle.solver import EntropySolver
from doddle.views import RunReporter
from doddle.words import Word, WordSeries

from .fake_dictionary import load_test_dictionary


class TestEngine:
    @patch.object(EntropySolver, "get_best_guess")
    def test_engine_runs_to_completion(self, mock_get_best_guess) -> None:
        # Arrange
        size = 5
        soln = Word("FUNKY")
        dictionary = load_test_dictionary(size)
        scorer = Scorer(size)
        histogram_builder = HistogramBuilder(scorer, dictionary.all_words, dictionary.common_words)
        solver = EntropySolver(histogram_builder)
        reporter = RunReporter()
        sut = Engine(dictionary, scorer, histogram_builder, solver, reporter)

        mock_get_best_guess.side_effect = [
            EntropyGuess(Word("MULCH"), False, 5),
            EntropyGuess(Word("FANGO"), False, 5),
            EntropyGuess(soln, True, 5),
        ]

        # Act
        game = sut.run(soln, [])

        # Assert
        assert game.is_solved

    @patch.object(EntropySolver, "get_best_guess")
    def test_engine_raises_error_if_non_convergent(self, mock_get_best_guess) -> None:
        # Arrange
        size = 5
        soln = Word("FUNKY")
        dictionary = load_test_dictionary(size)
        scorer = Scorer(size)
        histogram_builder = HistogramBuilder(scorer, dictionary.all_words, dictionary.common_words)
        solver = EntropySolver(histogram_builder)
        reporter = RunReporter()
        sut = Engine(dictionary, scorer, histogram_builder, solver, reporter)

        mock_get_best_guess.side_effect = [EntropyGuess(Word("MULCH"), False, 5)] * 25

        # Act + Assert
        with pytest.raises(FailedToFindASolutionError):
            sut.run(soln, [Word("STOLE")])


class TestSimulEngine:
    @patch.object(MinimaxSimulSolver, "get_best_guess")
    def test_engine_runs_to_completion(self, mock_get_best_guess) -> None:
        # Arrange
        size = 5
        solns = [
            Word("STICK"),
            Word("SNAKE"),
            Word("FLAME"),
            Word("TOWER"),
        ]

        dictionary = load_test_dictionary(size)
        scorer = Scorer(size)
        histogram_builder = HistogramBuilder(scorer, dictionary.all_words, dictionary.common_words)
        solver = MinimaxSimulSolver(histogram_builder)
        reporter = RunReporter()
        sut = SimulEngine(dictionary, scorer, histogram_builder, solver, reporter)

        mock_get_best_guess.side_effect = [
            MinimaxGuess(Word("STINK"), False, 5, 5),
            MinimaxGuess(solns[3], False, 5, 5),
            MinimaxGuess(solns[0], False, 5, 5),
            MinimaxGuess(solns[2], False, 5, 5),
            MinimaxGuess(solns[1], False, 5, 5),
        ]

        # Act
        game = sut.run(solns, [])

        # Assert
        assert game.is_solved

    @patch.object(MinimaxSimulSolver, "get_best_guess")
    def test_engine_raises_error_if_non_convergent(self, mock_get_best_guess) -> None:
        # Arrange
        size = 5
        solns = [
            Word("STICK"),
            Word("SNAKE"),
            Word("FLAME"),
            Word("TOWER"),
        ]

        dictionary = load_test_dictionary(size)
        scorer = Scorer(size)
        histogram_builder = HistogramBuilder(scorer, dictionary.all_words, dictionary.common_words)
        solver = MinimaxSimulSolver(histogram_builder)
        reporter = RunReporter()
        sut = SimulEngine(dictionary, scorer, histogram_builder, solver, reporter)

        mock_get_best_guess.side_effect = [MinimaxGuess(Word("MULCH"), False, 3, 5)] * 50

        # Act + Assert
        with pytest.raises(FailedToFindASolutionError):
            sut.run(solns, [Word("STOLE")])


class TestBenchmarker:
    @patch.object(factory, "load_dictionary")
    @patch.object(ProcessPoolExecutor, "map")
    def test_benchmark(self, patch_map: MagicMock, patch_load_dictionary: MagicMock) -> None:

        # Arrange
        def game_factory(f, solns: WordSeries, chunksize: int) -> Iterable[Game]:
            for soln in solns:
                game = Game(WordSeries([soln.value]), soln, [])
                game.is_solved = True
                game.scoreboard.add_row(1, soln, Word("GUESS"), "20101", 125)
                game.scoreboard.add_row(2, soln, soln, "22222", 1)
                yield game

        patch_load_dictionary.return_value = load_test_dictionary()
        patch_map.side_effect = game_factory

        sut = factory.create_benchmarker(5)
        solns = sut.engine.dictionary.common_words

        # Act
        games = sut.run_benchmark([])

        # Assert
        patch_map.assert_called_once_with(ANY, solns, chunksize=20)
        assert len(games) == len(solns)
        assert all((game.is_solved for game in games))


class TestSimulBenchmarker:
    @patch.object(factory, "load_dictionary")
    @patch.object(ProcessPoolExecutor, "map")
    def test_benchmark(self, patch_map: MagicMock, patch_load_dictionary: MagicMock) -> None:

        # Arrange
        num_simul = 4
        num_runs = 100
        patch_load_dictionary.return_value = load_test_dictionary()

        sut = factory.create_simul_benchmarker(5)
        solns = sut.engine.dictionary.common_words

        def game_factory(
            f, solns_factory: Iterable[list[Word]], chunksize: int
        ) -> Iterable[SimultaneousGame]:

            for game_solns in solns_factory:
                game = SimultaneousGame(solns, game_solns, [])
                game.is_solved = True
                yield game

        patch_map.side_effect = game_factory

        # Act
        games = sut.run_benchmark([], num_simul, num_runs)

        # Assert
        patch_map.assert_called_once_with(ANY, ANY, chunksize=20)
        assert len(games) == 100
        assert all((game.is_solved for game in games))
