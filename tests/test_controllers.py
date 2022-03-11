from unittest.mock import patch

from doddle.controllers import HideController, SolveController
from doddle.guess import MinimaxGuess
from doddle.histogram import HistogramBuilder
from doddle.scoring import Scorer, from_ternary
from doddle.solver import MinimaxSolver
from doddle.views import HideView, SolveView
from doddle.words import Word, load_dictionary


class TestSolveController:
    @patch.object(SolveView, "get_user_score")
    @patch.object(MinimaxSolver, "get_best_guess")
    def test_solve_feasible(self, mock_get_best_guess, mock_get_user_score) -> None:

        # Arrange
        size = 5
        dictionary = load_dictionary(size)
        scorer = Scorer(size)
        histogram_builder = HistogramBuilder(scorer, dictionary.all_words, dictionary.common_words)
        solver = MinimaxSolver(histogram_builder)
        view = SolveView(size)

        # Mocking
        def get_user_score(guess: Word) -> tuple[int, Word]:
            ternary_by_guess = {
                Word("RAISE"): "00000",
                Word("BLUDY"): "00000",
                Word("NOTCH"): "12102",
                Word("MONTH"): "22222",
            }
            score = from_ternary(ternary_by_guess[guess])
            return (score, guess)

        mock_get_user_score.side_effect = get_user_score
        mock_get_best_guess.side_effect = [
            MinimaxGuess(Word("BLUDY"), True, 10, 12),
            MinimaxGuess(Word("NOTCH"), True, 10, 1),
            MinimaxGuess(Word("MONTH"), True, 10, 1),
        ]

        sut = SolveController(dictionary, scorer, histogram_builder, solver, view)

        # Act
        is_solved = sut.solve(None)

        # Assert
        assert is_solved

    @patch.object(SolveView, "get_user_score")
    @patch.object(MinimaxSolver, "get_best_guess")
    def test_solve_infeasible(self, mock_get_best_guess, mock_get_user_score) -> None:
        def get_user_score(guess: Word) -> tuple[int, Word]:
            score = from_ternary("00000")
            return (score, guess)

        mock_get_user_score.side_effect = get_user_score
        mock_get_best_guess.side_effect = [
            MinimaxGuess(Word("BLUDY"), True, 10, 12),
            MinimaxGuess(Word("NOTCH"), True, 10, 1),
            MinimaxGuess(Word("MONTH"), True, 10, 1),
        ]

        # solver.get_best_guess(all_words, available_answers)

        # Arrange
        size = 5
        dictionary = load_dictionary(size)
        scorer = Scorer(size)
        histogram_builder = HistogramBuilder(scorer, dictionary.all_words, dictionary.common_words)
        solver = MinimaxSolver(histogram_builder)
        view = SolveView(size)

        sut = SolveController(dictionary, scorer, histogram_builder, solver, view)

        # Act
        is_solved = sut.solve(None)

        # Assert
        assert not is_solved


class TestHideController:
    @patch.object(HideView, "get_user_guess")
    def test_solve_feasible(self, mock_get_user_guess) -> None:

        # Arrange
        size = 5
        dictionary = load_dictionary(size)
        scorer = Scorer(size)
        histogram_builder = HistogramBuilder(scorer, dictionary.all_words, dictionary.common_words)
        view = HideView(size)

        # Mocking
        mock_get_user_guess.side_effect = [
            Word("SNAKE"),
            Word("MOUNT"),
            Word("CHILD"),
            Word("ARROW"),
            Word("BILLY"),
            Word("FILLY"),
        ]

        sut = HideController(dictionary, scorer, histogram_builder, view)

        # Act
        sut.hide(None)

        # Assert
        mock_get_user_guess.assert_called()
