from argparse import ArgumentParser, Namespace

from .model import Solver
from .scoring import Scorer
from .view import ConsoleView, RunView
from .words import WordLoader


def evade(args: Namespace) -> None:

    size = args.size or len(args.guess)
    best_guess = args.guess or Solver.seed(size)

    loader = WordLoader(size)
    scorer = Scorer(size)
    solver = Solver(scorer)

    available_answers = loader.common_words

    while True:
        solutions_by_score = solver.get_possible_solutions_by_score(available_answers, best_guess)
        highest_score = max(solutions_by_score, key=lambda k: len(solutions_by_score[k]))
        padded_score = f"{highest_score}".zfill(size)
        print(f"The score was {padded_score}")
        if scorer.is_perfect_score(highest_score):
            print("You win!")
            break

        available_answers = solutions_by_score[highest_score]
        best_guess = input("Please enter your next guess:\n").upper()


def solve(args: Namespace) -> None:

    size = args.size or len(args.guess)
    best_guess = args.guess or Solver.seed(size)

    view = ConsoleView(size)
    loader = WordLoader(size)
    scorer = Scorer(size)
    solver = Solver(scorer)

    all_words = loader.all_words
    available_answers = loader.common_words

    while True:
        (observed_score, best_guess) = view.get_user_score(best_guess)
        if scorer.is_perfect_score(observed_score):
            print("\nGreat success! ✨ 🔮 ✨")
            break

        histogram = solver.get_possible_solutions_by_score(available_answers, best_guess)
        available_answers = histogram[observed_score]
        best_guess = solver.get_best_guess(available_answers, all_words)
        print(f"\nThe best guess is {best_guess}")


def run(args: Namespace) -> None:

    solution = args.answer
    size = len(solution)
    best_guess = args.guess or Solver.seed(size)

    view = RunView(size)
    loader = WordLoader(size)
    scorer = Scorer(size)
    solver = Solver(scorer)

    all_words = loader.all_words
    available_answers = loader.common_words

    while True:
        observed_score = scorer.score_word(solution, best_guess)
        histogram = solver.get_possible_solutions_by_score(available_answers, best_guess)
        available_answers = histogram[observed_score]
        view.report_score(solution, best_guess, observed_score, available_answers)
        if best_guess == solution:
            break

        best_guess = solver.get_best_guess(available_answers, all_words)


def main() -> None:

    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--answer", required=True, type=lambda s: s.upper())
    run_parser.add_argument("--guess", type=lambda s: s.upper())
    run_parser.set_defaults(func=run)

    solve_parser = subparsers.add_parser("solve")
    solve_group = solve_parser.add_mutually_exclusive_group()
    solve_group.add_argument("--guess", type=lambda s: s.upper())
    solve_group.add_argument("--size", type=int)
    solve_parser.set_defaults(func=solve)

    evade_parser = subparsers.add_parser("evade")
    evade_group = evade_parser.add_mutually_exclusive_group()
    evade_group.add_argument("--guess", type=lambda s: s.upper())
    evade_group.add_argument("--size", type=int)
    evade_parser.set_defaults(func=evade)

    args = parser.parse_args()
    args.func(args)
