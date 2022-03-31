from __future__ import annotations

from dataclasses import dataclass

from .exceptions import FailedToFindASolutionError
from .game import Game, SimultaneousGame
from .histogram import HistogramBuilder
from .scoring import Scorer
from .simul_solver import SimulSolver
from .solver import Solver
from .views import RunReporter
from .words import Dictionary, Word


@dataclass
class Engine:
    """Primary class for running a Doddle game."""

    dictionary: Dictionary
    scorer: Scorer
    histogram_builder: HistogramBuilder
    solver: Solver
    reporter: RunReporter

    def run(self, solution: Word, user_guesses: list[Word]) -> Game:
        """Runs a Doddle game.

        Args:
            solution (Word): The solution
            user_guesses (list[Word]): A list of user-supplied, opening guesses

        Raises:
            FailedToFindASolutionError: If no solution is found

        Returns:
            Game: A Game object summarising the simulation.
        """

        all_words, available_answers = self.dictionary.words
        game = Game(available_answers, solution, user_guesses)
        guess = game.user_guess(0) or self.solver.seed(all_words.word_length)

        MAX_ITERS = 20
        for i in range(1, MAX_ITERS + 1):
            histogram = self.histogram_builder.get_solns_by_score(available_answers, guess)
            score = self.scorer.score_word(solution, guess)
            available_answers = histogram[score]
            game.update(i, guess, score, available_answers)
            self.reporter.display(game)

            if game.is_solved:
                return game

            guess = game.user_guess(i) or self.solver.get_best_guess(all_words, available_answers).word

        raise FailedToFindASolutionError(f"Failed to converge after {MAX_ITERS} iterations.")


@dataclass
class SimulEngine:
    """Primary class for running a simultaneous Doddle game."""

    dictionary: Dictionary
    scorer: Scorer
    histogram_builder: HistogramBuilder
    solver: SimulSolver
    reporter: RunReporter

    def run(self, solns: list[Word], user_guesses: list[Word]) -> SimultaneousGame:
        """Runs a simultaneous Doddle game.

        Args:
            solns (list[Word]): The solutions to each game
            user_guesses (list[Word]): The list of user-supplied, opening guesses

        Raises:
            FailedToFindASolutionError: If no solution is found

        Returns:
            SimultaneousGame: A SimultaneousGame object summarising the simulation
        """
        all_words, common_words = self.dictionary.words
        simul_game = SimultaneousGame(common_words, solns, user_guesses)
        guess = simul_game.user_guess(0) or self.solver.seed(all_words.word_length)

        MAX_ITERS = 20 + len(solns)
        for i in range(1, MAX_ITERS + 1):
            for game in simul_game:
                if game.is_solved:
                    continue
                available_answers = game.potential_solns
                histogram = self.histogram_builder.get_solns_by_score(available_answers, guess)
                score = self.scorer.score_word(game.soln, guess)
                new_available_answers = histogram[score]
                simul_game.update(i, game, guess, score, new_available_answers)

            self.reporter.display(simul_game)

            if simul_game.is_solved:
                return simul_game

            guess = simul_game.user_guess(i) or self.solver.get_best_guess(all_words, simul_game).word

        raise FailedToFindASolutionError(f"Failed to converge after {MAX_ITERS} iterations.")
