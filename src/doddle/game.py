from __future__ import annotations

from typing import Iterator, Protocol

from .scoring import to_ternary
from .view_models import Scoreboard, ScoreboardRow
from .words import Word, WordSeries


class DoddleGame(Protocol):
    word_length: int
    scoreboard: Scoreboard
    rounds: int
    is_solved: bool


class Game:
    def __init__(self, potential_solns: WordSeries, soln: Word | None = None) -> None:
        self.available_answers = potential_solns
        self.soln = soln
        self.scoreboard = Scoreboard()
        self.is_solved = False
        self.word_length = potential_solns.word_length

    def update(self, n: int, guess: Word, score: int, available_answers: WordSeries) -> ScoreboardRow:
        ternary_score = to_ternary(score, self.word_length)
        self.available_answers = available_answers
        row = self.scoreboard.add_row(n, self.soln, guess, ternary_score, len(available_answers))
        self.is_solved = all([s == "2" for s in list(ternary_score)])
        return row

    @property
    def num_remaining_answers(self) -> int:
        return len(self.available_answers)

    @property
    def rounds(self) -> int:
        return self.scoreboard.rows[-1].n if self.scoreboard.rows else 0


class SimultaneousGame:
    def __init__(self, potential_solns: WordSeries, solns: list[Word]) -> None:
        self.games = [Game(potential_solns, soln) for soln in solns]
        self.scoreboard = Scoreboard()

    @property
    def is_solved(self) -> bool:
        return all((g.is_solved for g in self.games))

    @property
    def word_length(self) -> int:
        return self.games[0].word_length

    @property
    def rounds(self) -> int:
        return self.scoreboard.rows[-1].n if self.scoreboard.rows else 0

    def update(
        self, n: int, game: Game, guess: Word, score: int, potential_solns: WordSeries
    ) -> ScoreboardRow:
        row = game.update(n, guess, score, potential_solns)
        self.scoreboard.rows.append(row)
        return row

    def __iter__(self) -> Iterator[Game]:
        return iter(self.games)
