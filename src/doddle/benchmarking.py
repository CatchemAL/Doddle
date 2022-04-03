from __future__ import annotations

import random
import typing
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import partial
from itertools import groupby
from math import sqrt
from typing import Callable, Iterable, Protocol, TypeVar

from tqdm import tqdm  # type: ignore

from .boards import Scoreboard, ScoreboardPrinter
from .decision import GraphBuilder
from .engine import Engine, SimulEngine
from .exceptions import InvalidWordleBotFileError
from .game import DoddleGame, Game, SimultaneousGame
from .histogram import HistogramBuilder
from .scoring import Scorer, to_ternary
from .words import Word, WordSeries

if typing.TYPE_CHECKING:
    from graphviz import Digraph  # type: ignore # pragma: no cover

TGame = TypeVar("TGame", bound=DoddleGame, covariant=True)


class __Printer(Protocol):
    def text(self, value: str) -> None:
        ...  # pragma: no cover


@dataclass
class Benchmark:
    guesses: list[Word]
    histogram: dict[int, int]
    scoreboards: list[Scoreboard]

    @property
    def opening_guess(self) -> Word:
        if self.guesses:
            return self.guesses[0]

        return self.scoreboards[0].rows[0].guess

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

    def to_csv(self, path: str) -> None:
        def solution(scoreboard: Scoreboard) -> str:
            return scoreboard.rows[0].soln.value

        ordered_scoreboards = sorted(self.scoreboards, key=solution)

        lines: list[str] = []
        for scoreboard in ordered_scoreboards:
            line = ",".join(str(row.guess) for row in scoreboard.rows)
            lines.append(line)

        contents = "\n".join(lines)

        self._write_to_file(path, contents)

    def digraph(self, *, predicate: Callable[[Scoreboard], bool] | None = None) -> "Digraph":

        if predicate:
            filtered_games = filter(predicate, self.scoreboards)
            builder = GraphBuilder(filtered_games)
        else:
            builder = GraphBuilder(self.scoreboards)

        return builder.build()

    def __repr__(self) -> str:
        n = self.num_games()
        num_guesses = self.num_guesses()
        mean = self.mean()
        return f"Benchmark (games={n}, guesses={num_guesses}, mean={mean:.4f})"

    def _repr_pretty_(self, p: __Printer, _: bool) -> None:
        printer = BenchmarkPrinter()
        text_display = printer.build_string(self)
        p.text(text_display)

    @staticmethod
    def _write_to_file(path: str, content: str) -> None:  # pragma: no cover
        with open(path, "w") as f:
            f.write(content)

    @classmethod
    def read_csv(cls, path: str, validate: bool = True) -> Benchmark:

        with open(path, "r") as file:
            raw = file.read()

        all_lines = [[Word(word) for word in line.split(",")] for line in raw.split("\n")]
        potential_solns = WordSeries([str(line[-1]) for line in all_lines])
        size = len(all_lines[0][0])
        scorer = Scorer(size)
        histogram_builder = HistogramBuilder(scorer, potential_solns, potential_solns)

        scoreboards: list[Scoreboard] = []
        histogram: defaultdict[int, int] = defaultdict(int)
        for guesses in all_lines:
            n = len(guesses)
            histogram[n] += 1
            soln = guesses[-1]
            scoreboard = Scoreboard()
            solns = potential_solns
            for i, guess in enumerate(guesses):
                score = scorer.score_word(soln, guess)
                solns_by_score = histogram_builder.get_solns_by_score(solns, guess)
                solns = solns_by_score[score]
                ternary = to_ternary(score, size)
                scoreboard.add_row(i + 1, soln, guess, ternary, len(solns))

            scoreboards.append(scoreboard)

        user_guesses: list[Word] = []
        benchmark = cls(user_guesses, histogram, scoreboards)

        if validate:
            benchmark.validate()

        return benchmark

    def validate(self) -> None:

        size = len(self.scoreboards[0].rows[0].score)

        def create_key(n: int):
            def score_path(scoreboard: Scoreboard) -> str:
                scores: list[str] = []
                for i in range(min(n, len(scoreboard.rows))):
                    score = scoreboard.rows[i].score
                    scores.append(score)
                return "-".join(scores)

            return score_path

        worst_num_rounds = max(scoreboard.rows[-1].n for scoreboard in self.scoreboards)
        sorted_boards = sorted(self.scoreboards, key=create_key(worst_num_rounds))

        for i in range(1, worst_num_rounds + 1):
            selector = create_key(i)
            grps = groupby(sorted_boards, key=selector)
            for _, grp in grps:
                inner_scoreboards = list(grp)
                if len(inner_scoreboards) == 1:
                    continue
                first_scoreboard = next(sb for sb in inner_scoreboards if len(sb) > i)
                first_follow_up_guess = first_scoreboard.rows[i].guess
                for scoreboard in inner_scoreboards:
                    follow_up_guess = scoreboard.rows[i].guess
                    if follow_up_guess != first_follow_up_guess:
                        printer = ScoreboardPrinter(size)
                        display1 = printer.build_string(first_scoreboard)
                        display2 = printer.build_string(scoreboard)
                        message = (
                            "Well this is awkward 😬. It seems as though the solver is not logically "
                            "consistent in how it plays each game - the same patterns seem to result "
                            "in different guesses which will result in non-deterministic outcomes and "
                            "a poorly defined decision tree. You can disable validation by passing "
                            "`validate=False` as an argument. However, it is strongly advised that you "
                            "check the solver for internal consistency.\n\nFor instance, please "
                            f"examine row {i+1} below for each game below:\n\n{display1}\n\n{display2}"
                        )
                        raise InvalidWordleBotFileError(message)


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

        scoreboards = [game.scoreboard for game in solved_games]
        benchmark = Benchmark(user_guesses, histogram, scoreboards)
        self.reporter.display(benchmark)
        return benchmark


@dataclass
class SimulBenchmarker:
    """A class to benchmark the performance of a Doddle SimulEngine"""

    engine: SimulEngine
    reporter: BenchmarkReporter

    def run_benchmark(
        self, user_guesses: list[Word], num_simul: int, num_runs: int = 1_000
    ) -> Benchmark:
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

        scoreboards = [game.scoreboard for game in solved_games]
        benchmark = Benchmark(user_guesses, histogram, scoreboards)
        self.reporter.display(benchmark)
        return benchmark


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


class BenchmarkReporter:
    def display(self, benchmark: Benchmark) -> None:
        printer = BenchmarkPrinter()
        report = printer.build_string(benchmark)
        print(report)


class NullBenchmarkReporter(BenchmarkReporter):
    """Null implementation of a RunReporter"""

    def display(self, _: Benchmark) -> None:
        """Does nothing"""
        pass
