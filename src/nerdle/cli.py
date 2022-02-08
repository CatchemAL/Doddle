from argparse import ArgumentParser, Namespace

from .factory import create_hide_controller, create_run_controller, create_solve_controller
from .solver import MinimaxSolver


def run(args: Namespace) -> None:

    solution = args.answer
    size = len(solution)
    best_guess = args.guess or MinimaxSolver.seed(size)
    controller = create_run_controller(size, args.depth)
    controller.run(solution, best_guess)


def solve(args: Namespace) -> None:

    size = args.size or len(args.guess)
    best_guess = args.guess or MinimaxSolver.seed(size)
    controller = create_solve_controller(size, args.depth)
    controller.solve(best_guess)


def hide(args: Namespace) -> None:

    size = args.size or len(args.guess)
    best_guess = args.guess or MinimaxSolver.seed(size)
    controller = create_hide_controller(size)
    controller.hide(best_guess)


def benchmark_performance(args: Namespace) -> None:
    print(f"Run benchmarks for size {args.size}")


def main() -> None:

    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--answer", required=True, type=lambda s: s.upper())
    run_parser.add_argument("--guess", type=lambda s: s.upper())
    run_parser.add_argument("--depth", required=False, default=1, type=int)
    run_parser.set_defaults(func=run)

    solve_parser = subparsers.add_parser("solve")
    solve_group = solve_parser.add_mutually_exclusive_group()
    solve_group.add_argument("--guess", type=lambda s: s.upper())
    solve_group.add_argument("--size", type=int)
    solve_parser.add_argument("--depth", required=False, default=1, type=int)
    solve_parser.set_defaults(func=solve)

    hide_parser = subparsers.add_parser("hide")
    hide_group = hide_parser.add_mutually_exclusive_group()
    hide_group.add_argument("--guess", type=lambda s: s.upper())
    hide_group.add_argument("--size", type=int, default=5)
    hide_parser.set_defaults(func=hide)

    benchmark_parser = subparsers.add_parser("benchmark")
    benchmark_parser.add_argument("--size", required=True, type=int)
    benchmark_parser.set_defaults(func=benchmark_performance)

    args = parser.parse_args()
    args.func(args)
