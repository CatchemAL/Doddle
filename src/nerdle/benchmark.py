from multiprocessing import Pool

from nerdle.solver import Solver
from nerdle.scoring import Scorer
from nerdle.words import WordLoader


def solve(solution):

    size = len(solution)
    best_guess = Solver.seed(size)

    loader = WordLoader(size)
    scorer = Scorer(size)
    solver = Solver(scorer)

    all_words = loader.all_words
    available_answers = loader.common_words

    n_guesses = 0

    while True:
        n_guesses += 1
        observed_score = scorer.score_word(solution, best_guess)
        histogram = solver.get_possible_solutions_by_score(available_answers, best_guess)
        available_answers = histogram[observed_score]
        if best_guess == solution:
            break

        best_guess = solver.get_best_guess(available_answers, all_words)

    return n_guesses


if __name__ == "__main__":

    size = 5
    processes = 8
    loader = WordLoader(size)
    solutions = loader.common_words

    counts = {}

    with Pool(processes) as p:
        n_guess = p.map(solve, solutions)

    for n in n_guess:
        counts[n] = counts.get(n, 0) + 1

    for c in sorted(counts):
        print(f"{c} guesses: {counts[c]}")
