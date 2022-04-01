from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from typing import Iterable
from unittest.mock import ANY, MagicMock, patch

from doddle import decision, factory
from doddle.benchmarking import Benchmark
from doddle.game import Game, SimultaneousGame
from doddle.words import Word, WordSeries

from .fake_dictionary import load_test_dictionary


class TestBenchmark:
    def test_statistics(self) -> None:
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
        mean = sut.mean()
        num_games = sut.num_games()
        num_guesses = sut.num_guesses()
        std = sut.std()

        # Assert
        assert mean == 2
        assert num_games == len(solns)
        assert num_guesses == 2 * num_games
        assert std == 0
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
        assert str_repr == "Benchmark (games=91, guesses=182, mean=2.0000)"

    def test_repr_pretty(self) -> None:
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

        sut = Benchmark(guesses, histogram, games)

        # Act
        sut._repr_pretty_(mock_printer, False)

        # Assert
        mock_printer.text.assert_called_once_with(expected[1:])

    @patch.object(decision, "digraph")
    def test_digraph(self, mock_digraph: MagicMock) -> None:
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
        mock_digraph.assert_called_once_with(games)

    @patch.object(decision, "digraph")
    def test_digraph_with_filter(self, mock_digraph: MagicMock) -> None:
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
        assert len(list(mock_digraph.call_args[0][0])) == len(game_words)


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
