import functools
from multiprocessing import Pool

from .controllers import RunController
from .words import WordLoader
from .views import SilentRunView


def benchmark(solver, size: int):

    loader = WordLoader(size)
    solutions = loader.common_words
    initial_guess = solver.seed(size)

    controller = RunController(loader, solver, SilentRunView())

    with Pool(8) as p:
        n_guess = p.map(functools.partial(controller.run, best_guess=initial_guess), solutions)

    # count occurrences of number of guesses to solve
    counts = {}
    for n in n_guess:
        counts[n] = counts.get(n, 0) + 1

    return counts
