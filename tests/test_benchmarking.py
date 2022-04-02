from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from typing import Iterable
from unittest.mock import ANY, MagicMock, PropertyMock, patch

import pytest

from doddle import benchmarking, decision, factory
from doddle.benchmarking import Benchmark, BenchmarkPrinter
from doddle.decision import GraphBuilder
from doddle.game import Game, SimultaneousGame
from doddle.words import Word, WordSeries

from .fake_dictionary import load_test_dictionary


class TestBenchmark:
    def test_statistics(self) -> None:
        # Arrange
        guesses = [Word("START"), Word("TOWER")]
        histogram = {1: 1, 2: 76, 3: 1256, 4: 1031, 5: 52}
        games: list[Game] = []

        sut = Benchmark(guesses, histogram, games)

        # Act
        mean = sut.mean()
        num_games = sut.num_games()
        num_guesses = sut.num_guesses()
        std = sut.std()

        # Assert
        assert mean == pytest.approx(3.4375, abs=1e-9)
        assert num_games == 2416
        assert num_guesses == 8305
        assert std == pytest.approx(0.595430481760274, abs=1e-9)
        assert sut.guesses == guesses
        assert sut.opening_guess == guesses[0]

    def test_repr(self) -> None:
        # Arrange
        def game_factory(solns: WordSeries) -> Iterable[Game]:
            for soln in solns:
                game = Game(WordSeries([soln.value]), soln, [])
                game.is_solved = True
                game.scoreboard.add_row(1, soln, Word("START"), "20101", 125)
                game.scoreboard.add_row(2, soln, soln, "22222", 1)
                yield game

        guesses = [Word("START")]
        histogram = {1: 1, 2: 76, 3: 1256, 4: 1031, 5: 52}
        solns = load_test_dictionary().common_words
        games = list(game_factory(solns))

        sut = Benchmark(guesses, histogram, games)

        # Act
        str_repr = repr(sut)
        print(str_repr)

        # Assert
        assert str_repr == "Benchmark (games=2416, guesses=8305, mean=3.4375)"

    @patch.object(BenchmarkPrinter, "build_string")
    def test_repr_pretty(self, patch_build_string: MagicMock) -> None:
        # Arrange
        guesses = [Word("START")]
        histogram = {1: 1, 2: 76, 3: 1256, 4: 1031, 5: 52}
        games = []

        mock_printer = MagicMock()
        mock_printer.text = MagicMock()

        expected = """
        1 |                    (1)
        2 | *                 (76)
        3 | ************   (1,262)
        4 | **********     (1,076)
        5 | *                 (52)

        Guess:    CRATE
        Games:    2,341
        Guesses:  8,912
        Mean:     3.429
        Std:      0.601"""

        patch_build_string.return_value = expected

        sut = Benchmark(guesses, histogram, games)

        # Act
        sut._repr_pretty_(mock_printer, False)

        # Assert
        mock_printer.text.assert_called_once_with(expected)

    @patch.object(benchmarking, "GraphBuilder")
    def test_digraph(self, mock_builder: MagicMock) -> None:
        # Arrange
        def game_factory(solns: WordSeries) -> Iterable[Game]:
            for soln in solns:
                game = Game(WordSeries([soln.value]), soln, [])
                game.is_solved = True
                game.scoreboard.add_row(1, soln, Word("START"), "20101", 125)
                game.scoreboard.add_row(2, soln, soln, "22222", 1)
                yield game

        guesses = [Word("START")]
        histogram = {1: 1, 2: 76, 3: 1256, 4: 1031, 5: 52}
        solns = load_test_dictionary().common_words
        games = list(game_factory(solns))
        sut = Benchmark(guesses, histogram, games)

        # Act
        sut.digraph()

        # Assert
        mock_builder.assert_called_once_with(games)

    @patch.object(benchmarking, "GraphBuilder")
    def test_digraph_with_filter(self, mock_builder: MagicMock) -> None:
        # Arrange
        def game_factory(solns: WordSeries) -> Iterable[Game]:
            for soln in solns:
                game = Game(WordSeries([soln.value]), soln, [])
                game.is_solved = True
                game.scoreboard.add_row(1, soln, Word("START"), "20101", 125)
                game.scoreboard.add_row(2, soln, soln, "22222", 1)
                yield game

        guesses = [Word("START")]
        histogram = {1: 1, 2: 76, 3: 1256, 4: 1031, 5: 52}
        solns = load_test_dictionary().common_words
        games = list(game_factory(solns))
        sut = Benchmark(guesses, histogram, games)

        game_words = {Word("RAISE"), Word("MOUNT"), Word("SNAKE")}

        def some_filter(game: Game) -> bool:
            return game.soln in game_words

        # Act
        sut.digraph(predicate=some_filter)

        # Assert
        assert len(list(mock_builder.call_args[0][0])) == len(game_words)


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


class TestBenchmarkPrinter:
    def test_build_string(self) -> None:
        # Arrange
        guesses = [Word("START")]
        histogram = {1: 1, 2: 76, 3: 1256, 4: 1031, 5: 52}
        games = []
        benchmark = Benchmark(guesses, histogram, games)
        sut = BenchmarkPrinter()

        expected = """
1 |                                                         (1)
2 | ***                                                    (76)
3 | **************************************************  (1,256)
4 | *****************************************           (1,031)
5 | **                                                     (52)

Guess:    START
Games:    2,416
Guesses:  8,305
Mean:     3.438
Std:      0.595
        """

        # Act
        actual = sut.build_string(benchmark)

        # Assert
        assert actual == expected.strip()

    @patch.object(Benchmark, "opening_guess", new_callable=PropertyMock)
    def test_describe(self, patch_opening_guess) -> None:
        # Arrange
        guesses = []
        histogram = {1: 1, 2: 76, 3: 1256, 4: 1031, 5: 52}
        games = []
        benchmark = Benchmark(guesses, histogram, games)
        sut = BenchmarkPrinter()

        patch_opening_guess.return_value = Word("CRATE")

        expected = """
Guess:    CRATE
Games:    2,416
Guesses:  8,305
Mean:     3.438
Std:      0.595
        """

        # Act
        actual = sut.describe(benchmark)

        # Assert
        assert actual.strip() == expected.strip()
