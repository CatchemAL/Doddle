from __future__ import annotations

from unittest.mock import patch

import pytest

from doddle.engine import Engine, SimulEngine
from doddle.exceptions import FailedToFindASolutionError
from doddle.guess import EntropyGuess, MinimaxGuess
from doddle.histogram import HistogramBuilder
from doddle.scoring import Scorer
from doddle.simul_solver import MinimaxSimulSolver
from doddle.solver import EntropySolver
from doddle.views import RunReporter
from doddle.words import Word

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
