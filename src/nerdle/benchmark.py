from collections import defaultdict
from multiprocessing import Pool
from typing import Callable, DefaultDict, Set


def benchmark(f: Callable[[str], int], solutions: Set[str]) -> DefaultDict[int, int]:

    with Pool(8) as p:
        n_guess = p.map(f, solutions)

    # count occurrences of number of guesses to solve
    histogram: DefaultDict[int, int] = defaultdict(int)
    for n in n_guess:
        histogram[n] += 1

    return histogram
