from argparse import ArgumentParser, Namespace

from .controllers import HideController, RunController, SolveController
from .scoring import Scorer
from .solver import Solver
from .views import HideView, RunView, SolveView
from .words import WordLoader


def run(args: Namespace) -> None:

    solution = args.answer
    size = len(solution)
    best_guess = args.guess or Solver.seed(size)

    loader = WordLoader(size)
    scorer = Scorer(size)
    solver = Solver(scorer)
    view = RunView(size)
    controller = RunController(loader, solver, view)

    controller.run(solution, best_guess)


def solve(args: Namespace) -> None:

    size = args.size or len(args.guess)
    best_guess = args.guess or Solver.seed(size)

    loader = WordLoader(size)
    scorer = Scorer(size)
    solver = Solver(scorer)
    view = SolveView(size)
    controller = SolveController(loader, solver, view)
    controller.solve(best_guess)


def hide(args: Namespace) -> None:

    size = args.size or len(args.guess)
    best_guess = args.guess or Solver.seed(size)

    loader = WordLoader(size)
    scorer = Scorer(size)
    solver = Solver(scorer)
    view = HideView(size)
    controller = HideController(loader, solver, view)
    controller.hide(best_guess)


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

    hide_parser = subparsers.add_parser("hide")
    hide_group = hide_parser.add_mutually_exclusive_group()
    hide_group.add_argument("--guess", type=lambda s: s.upper())
    hide_group.add_argument("--size", type=int)
    hide_parser.set_defaults(func=hide)

    args = parser.parse_args()
    args.func(args)
