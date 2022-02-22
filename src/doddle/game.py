from __future__ import annotations

from typing import Iterator, Protocol

from .scoring import to_ternary
from .view_models import Scoreboard, ScoreboardRow
from .words import Word, WordSeries


class DoddleGame(Protocol):
    word_length: int
    scoreboard: Scoreboard
    is_solved: bool

    @property
    def rounds(self) -> int:
        ...


class Game:
    def __init__(self, potential_solns: WordSeries, soln: Word) -> None:
        self.potential_solns = potential_solns
        self.soln = soln
        self.scoreboard = Scoreboard()
        self.is_solved = False
        self.word_length = potential_solns.word_length

    def update(self, n: int, guess: Word, score: int, potential_solns: WordSeries) -> ScoreboardRow:
        ternary_score = to_ternary(score, self.word_length)
        self.potential_solns = potential_solns
        row = self.scoreboard.add_row(n, self.soln, guess, ternary_score, len(potential_solns))
        self.is_solved = all([s == "2" for s in list(ternary_score)])
        return row

    @property
    def num_potential_solns(self) -> int:
        num_left = len(self.potential_solns)
        return num_left

    @property
    def rounds(self) -> int:
        return self.scoreboard.rows[-1].n if self.scoreboard.rows else 0


class SimultaneousGame:
    def __init__(self, potential_solns: WordSeries, solns: list[Word]) -> None:
        self.games = [Game(potential_solns, soln) for soln in solns]
        self.scoreboard = Scoreboard()
        self.is_solved = False
        self.word_length = potential_solns.word_length

    @property
    def rounds(self) -> int:
        return self.scoreboard.rows[-1].n if self.scoreboard.rows else 0

    def update(
        self, n: int, game: Game, guess: Word, score: int, potential_solns: WordSeries
    ) -> ScoreboardRow:
        row = game.update(n, guess, score, potential_solns)
        self.scoreboard.rows.append(row)
        self.is_solved = all((g.is_solved for g in self.games))
        return row

    def __iter__(self) -> Iterator[Game]:
        return iter(self.games)
