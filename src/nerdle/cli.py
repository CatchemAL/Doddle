from argparse import ArgumentParser, Namespace

from .factory import (
    create_benchmark_controller,
    create_hide_controller,
    create_run_controller,
    create_solve_controller,
)
from .solver import MinimaxSolver
from .words import Word


def run(args: Namespace) -> None:

    solution = args.answer
    size = len(solution)
    best_guess = args.guess or MinimaxSolver.seed(size)
    controller = create_run_controller(size, args.depth)
    controller.run(solution, best_guess)


def solve(args: Namespace) -> None:

    size = len(args.guess) if args.guess else args.size
    best_guess = args.guess or MinimaxSolver.seed(size)
    controller = create_solve_controller(size, args.depth)
    controller.solve(best_guess)


def hide(args: Namespace) -> None:

    size = len(args.guess) if args.guess else args.size
    controller = create_hide_controller(size)
    controller.hide(args.guess)


def benchmark_performance(args: Namespace) -> None:

    size = len(args.guess) if args.guess else args.size
    initial_guess = args.guess or MinimaxSolver.seed(size)
    controller = create_benchmark_controller(args.size, args.depth)
    controller.run(initial_guess)


def main() -> None:

    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--answer", required=True, type=Word)
    run_parser.add_argument("--guess", type=Word)
    run_parser.add_argument("--depth", required=False, default=1, type=int)
    run_parser.set_defaults(func=run)

    solve_parser = subparsers.add_parser("solve")
    solve_group = solve_parser.add_mutually_exclusive_group()
    solve_group.add_argument("--guess", type=lambda s: s.upper())
    solve_group.add_argument("--size", type=int, default=5)
    solve_parser.add_argument("--depth", required=False, default=1, type=int)
    solve_parser.set_defaults(func=solve)

    hide_parser = subparsers.add_parser("hide")
    hide_group = hide_parser.add_mutually_exclusive_group()
    hide_group.add_argument("--guess", type=lambda s: s.upper())
    hide_group.add_argument("--size", type=int, default=5)
    hide_parser.set_defaults(func=hide)

    benchmark_parser = subparsers.add_parser("benchmark")
    benchmark_group = benchmark_parser.add_mutually_exclusive_group()
    benchmark_group.add_argument("--guess", type=lambda s: s.upper())
    benchmark_group.add_argument("--size", type=int, default=5)
    benchmark_parser.add_argument("--depth", required=False, default=1, type=int)
    benchmark_parser.set_defaults(func=benchmark_performance)

    args = parser.parse_args()
    args.func(args)
