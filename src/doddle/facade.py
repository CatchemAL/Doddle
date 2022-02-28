from typing import Sequence, TypeVar
from .view_models import Scoreboard

from .enums import SolverType
from .factory import create_engine
from .views import NullRunView, RunView
from .words import Word

WordType = TypeVar("WordType", str, Word)


class Doddle:
    def __init__(
        self,
        size: int = 5,
        solver_type: SolverType = SolverType.MINIMAX,
        depth: int = 1,
        extras: Sequence[Word] | None = None,
        lazy_eval: bool = True,
        reporter: RunView | None = None,
    ):
        self.size = size

        self.engine = create_engine(
            size,
            solver_type=solver_type,
            depth=depth,
            extras=extras,
            lazy_eval=lazy_eval,
            reporter=reporter if reporter else NullRunView(),
        )

    def __call__(
        self, answer: WordType, guess: WordType | Sequence[WordType] | None = None
    ) -> Scoreboard:

        if answer is None:
            raise TypeError("Answer cannot be None")
        if isinstance(answer, WordType.__constraints__):
            soln = Word(answer)
        else:
            message = "The answer but be a valid WordType. Please supply either a string or a word."
            raise TypeError(message)

        if not guess:
            guesses: list[Word] = []
        elif isinstance(guess, WordType.__constraints__):
            guesses = [Word(guess)]
        else:
            guesses = [Word(g) for g in guess]

        if len(soln) != self.size:
            message = f'Expected an answer of size {self.size} but answer, {soln}, is of size {len(soln)}. '
            message += "To play Doddle with custom word lengths, please use the size argument when "
            message += "instantiating the Doddle object.\n\n"
            message += f"e.g.\n    doddle = Doddle(size={len(soln)})"
            raise ValueError(message)

        missized_words = [g.value for g in guesses if len(g) != self.size]
        if missized_words:
            message = f'All guesses must be of size {self.size}: ({", ".join(missized_words)}). '
            message += "To play Doddle with custom word lengths, please use the size argument when "
            message += "instantiating the Doddle object.\n\n"
            message += f"e.g.\n    doddle = Doddle(size={len(soln)})"
            raise ValueError(message)


        score_matrix = self.engine.histogram_builder.score_matrix
        if soln not in score_matrix.potential_solns:
            message = f"The answer {answer} is not known to Doddle. "
            message += "To play Doddle with custom words, please use the extras argument when "
            message += "instantiating the Doddle object.\n\n"
            message += f"e.g.\n    doddle = Doddle(size={len(answer)}, ..., extras=['{answer}'], ...)"
            raise ValueError(message)

        unknown_words = [g.value for g in guesses if g not in score_matrix.all_words]
        if unknown_words:
            missing = ", ".join(unknown_words)
            missing_extras = "', '".join(unknown_words)
            message = f"The following guesses are not known to Doddle: {missing}\n"
            message += "To play Doddle with custom words, please use the extras argument when "
            message += "instantiating the Doddle object.\n\n"
            message += f"e.g.\n    doddle = Doddle(size={len(answer)}, ..., extras=['{missing_extras}'], ...)"
            raise ValueError(message)

        game = self.engine.run(soln, guesses)
        return game.scoreboard
