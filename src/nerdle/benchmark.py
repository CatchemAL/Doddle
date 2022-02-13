from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from typing import Callable, DefaultDict, Set


def benchmark(f: Callable[[str], int], solutions: Set[str]) -> DefaultDict[int, int]:

    with ProcessPoolExecutor(max_workers=8) as executor:
        n_guess = executor.map(f, solutions)

    # count occurrences of number of guesses to solve
    histogram: DefaultDict[int, int] = defaultdict(int)
    for n in n_guess:
        histogram[n] += 1

    return histogram
