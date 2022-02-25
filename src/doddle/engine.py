from __future__ import annotations

import random
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import partial
from typing import Iterable

from .exceptions import FailedToFindASolutionError
from .game import Game, SimultaneousGame
from .histogram import HistogramBuilder
from .scoring import Scorer
from .simul_solver import SimulSolver
from .solver import Solver
from .views import BenchmarkView, RunView
from .words import Dictionary, Word


@dataclass
class Engine:

    dictionary: Dictionary
    scorer: Scorer
    histogram_builder: HistogramBuilder
    solver: Solver
    reporter: RunView

    def run(self, solution: Word, first_guess: Word | None) -> Game:
        all_words, available_answers = self.dictionary.words
        guess = first_guess or self.solver.seed(all_words.word_length)
        game = Game(available_answers, solution)

        MAX_ITERS = 15
        for i in range(MAX_ITERS):
            histogram = self.histogram_builder.get_solns_by_score(available_answers, guess)
            score = self.scorer.score_word(solution, guess)
            available_answers = histogram[score]
            game.update(i, guess, score, available_answers)
            self.reporter.display(game)

            if game.is_solved:
                return game

            guess = self.solver.get_best_guess(all_words, available_answers).word

        raise FailedToFindASolutionError(f"Failed to converge after {MAX_ITERS} iterations.")


@dataclass
class SimulEngine:

    dictionary: Dictionary
    scorer: Scorer
    histogram_builder: HistogramBuilder
    solver: SimulSolver
    reporter: RunView

    def run(self, solns: list[Word], first_guess: Word | None) -> SimultaneousGame:
        all_words, common_words = self.dictionary.words
        guess = first_guess or self.solver.seed(all_words.word_length)
        games = SimultaneousGame(common_words, solns)

        MAX_ITERS = 15
        for i in range(MAX_ITERS):
            for game in games:
                if game.is_solved:
                    continue
                available_answers = game.potential_solns
                histogram = self.histogram_builder.get_solns_by_score(available_answers, guess)
                score = self.scorer.score_word(game.soln, guess)
                new_available_answers = histogram[score]
                games.update(i, game, guess, score, new_available_answers)

            self.reporter.display(games)

            if games.is_solved:
                return games

            guess = self.solver.get_best_guess(all_words, games).word

        raise FailedToFindASolutionError(f"Failed to converge after {MAX_ITERS} iterations.")


class Benchmarker:
    def __init__(self, engine: Engine, reporter: BenchmarkView) -> None:
        self.engine = engine
        self.reporter = reporter

    def run_benchmark(self, first_guess: Word | None) -> None:

        dictionary = self.engine.dictionary
        f = partial(self.engine.run, first_guess=first_guess)

        with ProcessPoolExecutor(max_workers=8) as executor:
            games = executor.map(f, dictionary.common_words)

        histogram: defaultdict[int, int] = defaultdict(int)
        for game in games:
            histogram[game.rounds] += 1

        self.reporter.display(histogram)


class SimulBenchmarker:
    def __init__(self, engine: SimulEngine, reporter: BenchmarkView) -> None:
        self.engine = engine
        self.reporter = reporter

    def run_benchmark(self, first_guess: Word | None, num_simul: int, num_runs: int = 100) -> None:

        random.seed(13)

        dictionary = self.engine.dictionary
        f = partial(self.engine.run, first_guess=first_guess)

        def generate_games() -> Iterable[list[Word]]:
            dict_size = len(dictionary.common_words)
            for _ in range(num_runs):
                solns: list[Word] = []
                for _ in range(num_simul):
                    idx = random.randrange(dict_size)
                    soln = dictionary.common_words.iloc[idx]
                    solns.append(soln)
                yield solns

        game_factory = generate_games()

        with ProcessPoolExecutor(max_workers=8) as executor:
            games = executor.map(f, game_factory)

        histogram: defaultdict[int, int] = defaultdict(int)
        for game in games:
            histogram[game.rounds] += 1

        self.reporter.display(histogram)
