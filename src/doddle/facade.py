from __future__ import annotations

from typing import Sequence, Union

from .benchmarking import Benchmark, Benchmarker, NullBenchmarkReporter, SimulBenchmarker
from .boards import Scoreboard
from .engine import Engine, SimulEngine
from .enums import SolverType
from .factory import create_models
from .solver import EntropySolver
from .tree import TreeBuilder
from .views import NullRunReporter
from .words import Word

WordType = Union[str, Word]


class Doddle:
    """
    A simple, facade class for running Doddle simulations.

    Attributes:
      size (int, optional):
        The word length. Defaults to 5.

      solver_type (SolverType, optional):
        Enum stating the solver heuristic to use. Defaults to SolverType.MINIMAX.

      depth (int, optional):
        Depth of the search - how many moves to look ahead. Defaults to 1.

      extras (Sequence[Word] | Sequence[str] | None, optional):
        Any extra words to include in Doddle's dictionary. Defaults to None.

      lazy_eval (bool, optional):
        Whether to lazily score words as and when they are seen or to score every
        word against every word upfront. Lazy evaluation results in quicker
        initialisation but slower solves. The opposite is true when lazy initialisation
        is disabled. It is recommended to disable lazy evaluation if you plan to run
        Doddle multiple times within the same session for greater performance.
        Defaults to True.

      reporter (RunReporter | None, optional):
        A class that provided real-time reports (callback) as the solve progresses.
        Defaults to None.

    Methods
    -------
    __call__(answer, guess)
      Doddle is callable via:
        doddle = Doddle()
        scoreboard = doddle(answer=['SNAKE', 'FRUIT'], guess='APPLE')
    """

    def __init__(
        self,
        size: int = 5,
        solver_type: SolverType | str = SolverType.MINIMAX,
        depth: int = 1,
        extras: Sequence[Word] | Sequence[str] | None = None,
        lazy_eval: bool = True,
    ):
        """Initialises a new instance of a Doddle object.

        Args:
          size (int, optional):
            The word length. Defaults to 5.

          solver_type (SolverType | str, optional):
            Enum stating the solver heuristic to use. Defaults to SolverType.MINIMAX.

          depth (int, optional):
            Depth of the search - how many moves to look ahead. Defaults to 1.

          extras (Sequence[Word] | Sequence[str] | None, optional):
            Any extra words to include in Doddle's dictionary. Defaults to None.

          lazy_eval (bool, optional):
            Whether to lazily score words as and when they are seen or to score every
            word against every word upfront. Lazy evaluation results in quicker
            initialisation but slower solves. The opposite is true when lazy initialisation
            is disabled. It is recommended to disable lazy evaluation if you plan to run
            Doddle multiple times within the same session for greater performance.
            Defaults to True.

          reporter (RunReporter | None, optional):
            A class that provided real-time reports (callback) as the solve progresses.
            Defaults to None.
        """
        self.size = size
        e = [Word(extra) for extra in extras] if extras else []

        if isinstance(solver_type, str):
            solve_type = SolverType.from_str(solver_type)
        else:
            solve_type = solver_type

        dictionary, scorer, histogram_builder, solver, simul_solver = create_models(
            size,
            solver_type=solve_type,
            depth=depth,
            extras=e,
            lazy_eval=lazy_eval,
        )

        callback = NullRunReporter()
        benchmarkReporter = NullBenchmarkReporter()

        self.dictionary = dictionary
        self.scorer = scorer
        self.histogram_builder = histogram_builder
        self.engine = Engine(dictionary, scorer, histogram_builder, solver, callback)
        self.simul_engine = SimulEngine(dictionary, scorer, histogram_builder, simul_solver, callback)
        self.benchmarker = Benchmarker(self.engine, benchmarkReporter)
        self.simul_benchmarker = SimulBenchmarker(self.simul_engine, benchmarkReporter)

    def __call__(
        self, answer: WordType | Sequence[WordType], guess: WordType | Sequence[WordType] | None = None
    ) -> Scoreboard:
        """Callable that runs a Doddle game and returns the resulting scoreboard.

        Args:
          answer (WordType | Sequence[WordType]):
            A word intended to be the answer. Alternatively, a sequence of words
            if you wish to play Doddle in simultaneous mode.

          guess (WordType | Sequence[WordType] | None, optional):
            An optional word to be played as the opening guess. You can pass a list
            of guesses if you want to play several openers. Defaults to None.

        Raises:
          ValueError:
            If the provided words are invalid.

        Returns:
          Scoreboard:
            A scoreboard showing how the game played out.
        """

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

    def benchmark(self, guess: WordType | Sequence[WordType] | None = None) -> Benchmark:
        self.histogram_builder.score_matrix.precompute()

        guesses = self.__to_word_list(guess, "guess") if guess else []
        benchmark = self.benchmarker.run_benchmark(guesses)
        return benchmark

    def simul_benchmark(
        self, num_simul: int, num_rounds: int = 1000, guess: WordType | Sequence[WordType] | None = None
    ) -> Benchmark:
        self.histogram_builder.score_matrix.precompute()

        guesses = self.__to_word_list(guess, "guess") if guess else []
        benchmark = self.simul_benchmarker.run_benchmark(guesses, num_simul, num_rounds)
        return benchmark

    def tree_search(self, guess: WordType | None = None) -> Benchmark:
        self.histogram_builder.score_matrix.precompute()

        opening_guess = Word(guess) if guess else Word("SALET")
        common_words = self.dictionary.common_words
        solver = EntropySolver(self.histogram_builder)
        tree_builder = TreeBuilder(self.dictionary, self.scorer, self.histogram_builder, solver)
        root_node = tree_builder.build(common_words, opening_guess)
        comma_separated_values = root_node.csv(False)
        return Benchmark.from_csv(comma_separated_values, False)

    @staticmethod
    def __to_word_list(words: WordType | Sequence[WordType] | None, label: str) -> list[Word]:
        if words is None:
            raise TypeError(f"The {label} cannot be None.")

        if isinstance(words, Word) or isinstance(words, str):
            soln = Word(words)
            return [soln]

        return [Word(g) for g in words]
