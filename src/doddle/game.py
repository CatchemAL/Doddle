from __future__ import annotations

from typing import Iterator, Protocol

from .boards import Scoreboard, ScoreboardRow
from .scoring import to_ternary
from .words import Word, WordSeries


class DoddleGame(Protocol):
    """Protocol for a game of Doddle.

    Known implementations:
     - Game (a single game of Doddle)
     - SimultaneousGame (representation of many games played at once)
    """

    word_length: int
    scoreboard: Scoreboard
    is_solved: bool

    @property
    def rounds(self) -> int:
        """The number of rounds played to date in the current game.

        Returns:
            int: Return the number of rounds played to date in the current game.
        """
        ...

    def user_guess(self, n: int) -> Word | None:
        """Gets the nth user guess of None if not specified.

        Args:
            n (int): The nth round.

        Returns:
            Word | None: The nth user guess or None if not specified.
        """
        ...


class Game:
    """A representation of a single game of Doddle.

    Keeps track of key variables such as any user defined guesses
    and the real-time scoreboard.
    """

    def __init__(self, potential_solns: WordSeries, soln: Word, opening_guesses: list[Word]) -> None:
        """Initialises a new instance of the Game object.

        Args:
            potential_solns (WordSeries): Words that could be potential solutions to the current game.
            soln (Word): The actual solution to the game.
            opening_guesses (list[Word]): The user defined, opening guesses.
        """

        self.potential_solns = potential_solns
        self.soln = soln
        self.scoreboard = Scoreboard()
        self.is_solved = False
        self.word_length = potential_solns.word_length
        self.opening_guesses = opening_guesses

    def update(self, n: int, guess: Word, score: int, potential_solns: WordSeries) -> ScoreboardRow:
        """Updates the status of the game after each move is played.

        Args:
            n (int): The round (i.e. the nth guess in the current game).
            guess (Word): The guess on the nth round.
            score (int): A decimal representation of the ternary score.
            potential_solns (WordSeries): The potential solutions remaining, having played the guess.

        Returns:
            ScoreboardRow: The row added to the internal scoreboard.
        """
        ternary_score = to_ternary(score, self.word_length)
        self.potential_solns = potential_solns
        row = self.scoreboard.add_row(n, self.soln, guess, ternary_score, len(potential_solns))
        self.is_solved = all([s == "2" for s in list(ternary_score)])
        return row

    @property
    def num_potential_solns(self) -> int:
        """The number of remaining solutions.

        Returns:
            int: Returns the number of remaining solutions.
        """
        num_left = len(self.potential_solns)
        return num_left

    @property
    def rounds(self) -> int:
        """The number of rounds played to date in the current game.

        Returns:
            int: Return the number of rounds played to date in the current game.
        """
        return self.scoreboard.rows[-1].n if self.scoreboard.rows else 0

    def user_guess(self, n: int) -> Word | None:
        """Gets the nth user guess of None if not specified.

        Args:
            n (int): The nth round.

        Returns:
            Word | None: The nth user guess or None if not specified.
        """
        if n >= len(self.opening_guesses):
            return None
        return self.opening_guesses[n]


class SimultaneousGame:
    """A representation of a simultaneous game of Doddle.

    Keeps track of key variables such as any user defined guesses, the
    global real-time scoreboard and individual Game objects.
    """

    def __init__(self, potential_solns: WordSeries, solns: list[Word], user_guess: list[Word]) -> None:
        """Initialises a new instance of the SimultaneousGame object.

        Args:
            potential_solns (WordSeries): Words that could be potential solutions to the current game.
            solns (list[Word]): The actual solutions to each game.
            opening_guesses (list[Word]): The user defined, opening guesses.
        """

        self.games = [Game(potential_solns, soln, user_guess) for soln in solns]
        self.scoreboard = Scoreboard()
        self.is_solved = False
        self.word_length = potential_solns.word_length

    @property
    def rounds(self) -> int:
        """The number of rounds played to date in the current game.

        Returns:
            int: Return the number of rounds played to date in the current game.
        """
        return self.scoreboard.rows[-1].n if self.scoreboard.rows else 0

    def update(
        self, n: int, game: Game, guess: Word, score: int, potential_solns: WordSeries
    ) -> ScoreboardRow:
        """Updates the status of the game after each move is played.

        Args:
            n (int): The round (i.e. the nth guess in the current game).
            game (Game): The game to which each score is associated.
            guess (Word): The guess on the nth round.
            score (int): A decimal representation of the ternary score for the given game.
            potential_solns (WordSeries): The potential solutions remaining, having played the guess.

        Returns:
            ScoreboardRow: The row added to the internal scoreboard.
        """

        row = game.update(n, guess, score, potential_solns)
        self.scoreboard.rows.append(row)
        self.is_solved = all((g.is_solved for g in self.games))
        return row

    def __iter__(self) -> Iterator[Game]:
        """Gets an iterator for the individual Games.

        Returns:
            Iterator[Game]: The Game iterator.
        """
        return iter(self.games)

    def user_guess(self, n: int) -> Word | None:
        """Gets the nth user guess of None if not specified.

        Args:
            n (int): The nth round.

        Returns:
            Word | None: The nth user guess or None if not specified.
        """
        return self.games[0].user_guess(n)
