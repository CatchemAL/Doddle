import argparse
from argparse import Namespace
from .model import Solver, seed
from .scoring import Scorer
from .dictionary import WordLoader


def evade(args: Namespace):

    size = args.size or len(args.guess)
    best_guess = args.guess or seed(size)
    
    loader = WordLoader(size)
    scorer = Scorer(size)
    solver = Solver(scorer)

    available_answers = loader.common_words

    while True:
        solutions_by_score = solver.get_possible_solutions_by_score(available_answers, best_guess)
        highest_score = max(solutions_by_score, key=lambda k: len(solutions_by_score[k]))
        padded_score = f'{highest_score}'.zfill(size)
        print(f'The score was {padded_score}')
        if scorer.is_perfect_score(highest_score):
            print('You win!')
            break

        available_answers = solutions_by_score[highest_score]
        best_guess = input(f'Please enter your next guess:\n').upper()


def solve(args: Namespace):

    size = args.size or len(args.guess)
    best_guess = args.guess or seed(size)
    
    loader = WordLoader(size)
    scorer = Scorer(size)
    solver = Solver(scorer)

    all_words = loader.common_words.union(loader.all_words)
    available_answers = loader.common_words

    while True:
        observed_score = int(input(f'Enter observed score for {best_guess}:\n'))
        if scorer.is_perfect_score(observed_score):
            print('Great success!')
            break

        histogram = solver.get_possible_solutions_by_score(available_answers, best_guess)
        available_answers = histogram[observed_score]
        best_guess = solver.get_best_guess(available_answers, all_words)
        print(f'The best guess is {best_guess}')


def simulate(args: Namespace):

    solution = args.solution
    size = len(solution)
    best_guess = args.guess or seed(size)
    
    loader = WordLoader(size)
    scorer = Scorer(size)
    solver = Solver(scorer)

    all_words = loader.common_words.union(loader.all_words)
    available_answers = loader.common_words
    
    while True:
        solver.prettify(solution, best_guess)
        observed_score = scorer.score_word(solution, best_guess)
        if scorer.is_perfect_score(observed_score):
            break

        histogram = solver.get_possible_solutions_by_score(available_answers, best_guess)
        available_answers = histogram[observed_score]
        best_guess = solver.get_best_guess(available_answers, all_words)


def main() -> None:

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    simulate_parser = subparsers.add_parser('simulate')
    simulate_parser.add_argument("--solution", required=True, type=str)
    simulate_parser.add_argument("--guess", type=str)
    simulate_parser.set_defaults(func=simulate)
    
    solve_parser = subparsers.add_parser('solve')
    solve_group = solve_parser.add_mutually_exclusive_group()
    solve_group.add_argument("--guess", type=str)
    solve_group.add_argument("--size", type=int)
    solve_parser.set_defaults(func=solve)
    
    evade_parser = subparsers.add_parser('evade')
    evade_group = evade_parser.add_mutually_exclusive_group()
    evade_group.add_argument("--guess", type=str)
    evade_group.add_argument("--size", type=int)
    evade_parser.set_defaults(func=evade)
    
    args = parser.parse_args()
    args.func(args)
