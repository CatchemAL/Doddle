from __future__ import annotations

import random
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import partial
from typing import Iterable

from tqdm import tqdm  # type: ignore

from .engine import Engine, SimulEngine
from .game import Game, SimultaneousGame
from .views import BenchmarkReporter
from .words import Word


@dataclass
class Benchmarker:
    """A class to benchmark the performance of a Doddle engine"""

    engine: Engine
    reporter: BenchmarkReporter

    def run_benchmark(self, user_guesses: list[Word]) -> list[Game]:
        """Benchmarks an engine given a list of user-supplied, opening guesses.

        Args:
            user_guesses (list[Word]): The opening guesses.
        """
        dictionary = self.engine.dictionary
        f = partial(self.engine.run, user_guesses=user_guesses)

        total = len(dictionary.common_words)
        histogram: defaultdict[int, int] = defaultdict(int)
        solved_games: list[Game] = []
        with ProcessPoolExecutor() as executor:
            games = executor.map(f, dictionary.common_words, chunksize=20)
            for game in tqdm(games, total=total):
                solved_games.append(game)
                histogram[game.rounds] += 1

        self.reporter.display(histogram)
        return solved_games


@dataclass
class SimulBenchmarker:
    """A class to benchmark the performance of a Doddle SimulEngine"""

    engine: SimulEngine
    reporter: BenchmarkReporter

    def run_benchmark(
        self, user_guesses: list[Word], num_simul: int, num_runs: int = 1_000
    ) -> list[SimultaneousGame]:
        """Benchmarks a simul engine given a list of opening guesses.

        Args:
            user_guesses (list[Word]): The opening guesses.
            num_simul (int): The number of games to be played simultaneously.
            num_runs (int, optional): The number of runs in the benchmark. Defaults to 100.
        """
        random.seed(13)

        dictionary = self.engine.dictionary
        f = partial(self.engine.run, user_guesses=user_guesses)

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

        solved_games: list[SimultaneousGame] = []
        histogram: defaultdict[int, int] = defaultdict(int)
        with ProcessPoolExecutor() as executor:
            games = executor.map(f, game_factory, chunksize=20)
            for game in tqdm(games, total=num_runs):
                solved_games.append(game)
                histogram[game.rounds] += 1

        self.reporter.display(histogram)
        return solved_games
