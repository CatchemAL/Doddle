from typing import Sequence, Union

from .engine import Engine, SimulEngine
from .enums import SolverType
from .factory import create_models
from .view_models import Scoreboard
from .views import NullRunView, RunView
from .words import Word

WordType = Union[str, Word]


class Doddle:
    def __init__(
        self,
        size: int = 5,
        solver_type: SolverType = SolverType.MINIMAX,
        depth: int = 1,
        extras: Sequence[Word] | Sequence[str] | None = None,
        lazy_eval: bool = True,
        reporter: RunView | None = None,
    ):
        self.size = size
        e = [Word(extra) for extra in extras] if extras else []

        dictionary, scorer, histogram_builder, solver, simul_solver = create_models(
            size,
            solver_type=solver_type,
            depth=depth,
            extras=e,
            lazy_eval=lazy_eval,
        )

        callback = reporter if reporter else NullRunView()
        self.engine = Engine(dictionary, scorer, histogram_builder, solver, callback)
        self.simul_engine = SimulEngine(dictionary, scorer, histogram_builder, simul_solver, callback)
        self.dictionary = dictionary

    def __call__(
        self, answer: WordType | Sequence[WordType], guess: WordType | Sequence[WordType] | None = None
    ) -> Scoreboard:

        solns = self.__to_word_list(answer, "answer")
        guesses = self.__to_word_list(guess, "guess") if guess else []

        size = len(solns[0])

        missized_solns = [s.value for s in solns if len(s) != self.size]
        if missized_solns:
            message = f"All answers must be of length {self.size}: ({', '.join(missized_solns)}). "
            message += "To play Doddle with custom word lengths, please use the size argument when "
            message += "instantiating the Doddle object.\n\n"
            message += f"e.g.\n    doddle = Doddle(size={size})"
            raise ValueError(message)

        missized_guesses = [g.value for g in guesses if len(g) != self.size]
        if missized_guesses:
            message = f'All guesses must be of size {self.size}: ({", ".join(missized_guesses)}). '
            message += "To play Doddle with custom word lengths, please use the size argument when "
            message += "instantiating the Doddle object.\n\n"
            message += f"e.g.\n    doddle = Doddle(size={len(missized_guesses[0])})"
            raise ValueError(message)

        score_matrix = self.engine.histogram_builder.score_matrix

        unknown_solns = [s.value for s in solns if s not in score_matrix.potential_solns]
        if unknown_solns:
            missing = ", ".join(unknown_solns)
            missing_extras = "', '".join(unknown_solns)
            message = f"The following answers are not known to Doddle: {missing}\n"
            message += "To play Doddle with custom words, please use the extras argument when "
            message += "instantiating the Doddle object.\n\n"
            message += f"e.g.  doddle = Doddle(size={size}, ..., extras=['{answer}'])"
            raise ValueError(message)

        unknown_words = [g.value for g in guesses if g not in score_matrix.all_words]
        if unknown_words:
            missing = ", ".join(unknown_words)
            missing_extras = "', '".join(unknown_words)
            message = f"The following guesses are not known to Doddle: {missing}\n"
            message += "To play Doddle with custom words, please use the extras argument when "
            message += "instantiating the Doddle object.\n\n"
            message += f"e.g.  doddle = Doddle(size={size}, ..., extras=['{missing_extras}'])"
            raise ValueError(message)

        if len(solns) == 1:
            game = self.engine.run(solns[0], guesses)
            return game.scoreboard

        simul_game = self.simul_engine.run(solns, guesses)
        return simul_game.scoreboard

    @staticmethod
    def __to_word_list(words: WordType | Sequence[WordType] | None, label: str) -> list[Word]:
        if words is None:
            raise TypeError(f"The {label} cannot be None.")

        if isinstance(words, WordType):
            soln = Word(words)
            return [soln]

        return [Word(g) for g in words]
