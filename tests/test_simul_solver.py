from doddle.game import SimultaneousGame
from doddle.histogram import HistogramBuilder
from doddle.scoring import Scorer
from doddle.simul_solver import EntropySimulSolver, MinimaxSimulSolver
from doddle.words import Word

from .fake_dictionary import load_test_dictionary


class TestMinimaxSimulSolver:
    def test_simul_solver_get_best_guess(self) -> None:
        # Arrange
        solns = [
            Word("STICK"),
            Word("SNAKE"),
            Word("FLAME"),
            Word("TOWER"),
        ]

        dictionary = load_test_dictionary()
        scorer = Scorer(dictionary.word_length)
        histogram_builder = HistogramBuilder(scorer, dictionary.all_words, dictionary.common_words)
        sut = MinimaxSimulSolver(histogram_builder)

        games = SimultaneousGame(dictionary.common_words, solns, [])

        # Act
        simul_guess = sut.get_best_guess(dictionary.all_words, games)

        # Assert
        assert simul_guess.word == Word("LATER")

    def test_simul_solver_seeds(self) -> None:
        # Arrange
        dictionary = load_test_dictionary()
        scorer = Scorer(dictionary.word_length)
        histogram_builder = HistogramBuilder(scorer, dictionary.all_words, dictionary.common_words)
        sut = EntropySimulSolver(histogram_builder)

        expected = Word("SECRETION")

        # Act
        actual = sut.seed(9)

        # Assert
        assert actual == expected


class TestEntropySimulSolver:
    def test_simul_solver_get_best_guess(self) -> None:
        # Arrange
        solns = [
            Word("STICK"),
            Word("SNAKE"),
            Word("FLAME"),
            Word("TOWER"),
        ]

        dictionary = load_test_dictionary()
        scorer = Scorer(dictionary.word_length)
        histogram_builder = HistogramBuilder(scorer, dictionary.all_words, dictionary.common_words)
        sut = EntropySimulSolver(histogram_builder)

        games = SimultaneousGame(dictionary.common_words, solns, [])

        # Act
        simul_guess = sut.get_best_guess(dictionary.all_words, games)

        # Assert
        assert simul_guess.word == Word("RAISE")

    def test_simul_solver_seeds(self) -> None:
        # Arrange
        dictionary = load_test_dictionary()
        scorer = Scorer(dictionary.word_length)
        histogram_builder = HistogramBuilder(scorer, dictionary.all_words, dictionary.common_words)
        sut = EntropySimulSolver(histogram_builder)

        expected = Word("RAISE")

        # Act
        actual = sut.seed(5)

        # Assert
        assert actual == expected
