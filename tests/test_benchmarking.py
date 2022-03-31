from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from typing import Iterable
from unittest.mock import ANY, MagicMock, patch

from doddle import factory
from doddle.game import Game, SimultaneousGame
from doddle.words import Word, WordSeries

from .fake_dictionary import load_test_dictionary


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
        benchmark = sut.run_benchmark([])

        # Assert
        patch_map.assert_called_once_with(ANY, solns, chunksize=20)
        assert benchmark.opening_guess == Word("GUESS")
        assert benchmark.num_games() == len(solns)
        assert all((game.is_solved for game in benchmark.games))


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
