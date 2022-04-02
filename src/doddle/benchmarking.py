from __future__ import annotations

import random
import typing
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import partial
from math import sqrt
from typing import Callable, Iterable, Protocol

from tqdm import tqdm  # type: ignore

from .engine import Engine, SimulEngine
from .game import Game, SimultaneousGame
from .views import BenchmarkReporter
from .words import Word

if typing.TYPE_CHECKING:
    from graphviz import Digraph  # type: ignore # pragma: no cover


class __Printer(Protocol):
    def text(self, value: str) -> None:
        ...  # pragma: no cover


@dataclass
class Benchmark:
    guesses: list[Word]
    histogram: dict[int, int]
    games: list[Game]

    def num_games(self) -> int:
        return sum(self.histogram.values())

    def num_guesses(self) -> int:
        return sum(k * v for k, v in self.histogram.items())

    def mean(self) -> float:
        return self.num_guesses() / self.num_games()

    def std(self) -> float:

        n = self.num_games()
        mean = self.mean()

        mean_x_squared = sum(k * k * v for k, v in self.histogram.items()) / n
        variance = mean_x_squared - (mean * mean)

        return sqrt(variance)

    def digraph(self, *, predicate: Callable[[Game], bool] | None = None) -> "Digraph":
        from .decision import digraph

        if predicate:
            filtered_games = filter(predicate, self.games)
            return digraph(filtered_games)

        return digraph(self.games)

    @property
    def opening_guess(self) -> Word:
        if self.guesses:
            return self.guesses[0]

        first_game = self.games[0]
        return first_game.scoreboard.rows[0].guess

    def __repr__(self) -> str:
        n = self.num_games()
        num_guesses = self.num_guesses()
        mean = self.mean()
        return f"Benchmark (games={n}, guesses={num_guesses}, mean={mean:.4f})"

    def _repr_pretty_(self, p: __Printer, _: bool) -> None:
        printer = BenchmarkPrinter()
        text_display = printer.build_string(self)
        p.text(text_display)


@dataclass
class Benchmarker:
    """A class to benchmark the performance of a Doddle engine"""

    engine: Engine
    reporter: BenchmarkReporter

    def run_benchmark(self, user_guesses: list[Word]) -> Benchmark:
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
        return Benchmark(user_guesses, histogram, solved_games)


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


class BenchmarkPrinter:
    def build_string(self, benchmark: Benchmark) -> str:
        chart = self.bar_chart(benchmark.histogram)
        stats = self.describe(benchmark)
        return f"{chart}\n\n{stats}"

    @staticmethod
    def describe(benchmark: Benchmark) -> str:

        if benchmark.guesses:
            guess = ",".join(str(word) for word in benchmark.guesses)
        else:
            guess = str(benchmark.opening_guess)

        stats = f"""
Guess:    {guess}
Games:    {benchmark.num_games():,}
Guesses:  {benchmark.num_guesses():,}
Mean:     {benchmark.mean():.3f}
Std:      {benchmark.std():.3f}
        """

        return stats.strip()

    @staticmethod
    def bar_chart(histogram: dict[int, int]) -> str:

        CHARS = 50

        worst_score = max(histogram.keys())
        largest = max(histogram.values())
        increment = largest / CHARS

        stars: list[str] = []
        for i in range(worst_score):
            value = histogram.get(i + 1, 0)
            num = round(value / increment)
            stars.append("*" * num)

        max_stars = max(len(star) for star in stars)

        rows: list[str] = []
        for i, star in enumerate(stars):
            value = histogram.get(i + 1, 0)
            counts = f"({value:,})".rjust(9, " ")
            padded_star = star.ljust(max_stars, " ")
            row = f"{i+1} | {padded_star}{counts}"
            rows.append(row)

        return "\n".join(rows)
