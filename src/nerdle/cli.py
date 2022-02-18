from argparse import ArgumentParser, Namespace

from .controllers import HideController, SolveController
from .factory import create_benchmarker, create_models, create_simulator
from .solver import SolverType
from .views import HideView, SolveView
from .words import Word


def solve(args: Namespace) -> None:

    guess: Word | None = args.guess
    depth: int = args.depth
    solver_type: SolverType = args.solver
    size: int = len(guess) if guess else args.size

    dictionary, scorer, histogram_builder, solver = create_models(
        size, solver_type=solver_type, depth=depth, extras=[guess]
    )

    view = SolveView(size)
    controller = SolveController(dictionary, scorer, histogram_builder, solver, view)
    controller.solve(guess)


def hide(args: Namespace) -> None:

    guess: Word | None = args.guess
    size: int = len(guess) if guess else args.size

    dictionary, scorer, histogram_builder, _ = create_models(size, extras=[guess])

    view = HideView(size)
    controller = HideController(dictionary, scorer, histogram_builder, view)
    controller.hide(guess)


def run(args: Namespace) -> None:

    solution: Word = args.answer
    guess: Word | None = args.guess
    depth: int = args.depth
    solver_type: SolverType = args.solver
    size = len(solution)

    simulator = create_simulator(size, solver_type=solver_type, depth=depth, extras=[solution, guess])
    simulator.run(solution, guess)


def benchmark_performance(args: Namespace) -> None:

    guess: Word | None = args.guess
    depth: int = args.depth
    solver_type: SolverType = args.solver
    size: int = len(guess) if guess else args.size

    benchmarker = create_benchmarker(size, solver_type=solver_type, depth=depth, extras=[guess])
    benchmarker.run_benchmark(guess)


def main() -> None:

    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--answer", required=True, type=Word)
    run_parser.add_argument("--guess", type=Word)
    run_parser.add_argument("--solver", type=SolverType.from_str, default=SolverType.MINIMAX)
    run_parser.add_argument("--depth", required=False, default=1, type=int)
    run_parser.set_defaults(func=run)

    solve_parser = subparsers.add_parser("solve")
    solve_group = solve_parser.add_mutually_exclusive_group()
    solve_group.add_argument("--guess", type=Word)
    solve_group.add_argument("--size", required=False, type=int, default=5)
    solve_parser.add_argument("--solver", type=SolverType.from_str, default=SolverType.MINIMAX)
    solve_parser.add_argument("--depth", required=False, default=1, type=int)
    solve_parser.set_defaults(func=solve)

    hide_parser = subparsers.add_parser("hide")
    hide_group = hide_parser.add_mutually_exclusive_group()
    hide_group.add_argument("--guess", type=Word)
    hide_group.add_argument("--size", type=int, default=5)
    hide_parser.set_defaults(func=hide)

    benchmark_parser = subparsers.add_parser("benchmark")
    benchmark_group = benchmark_parser.add_mutually_exclusive_group()
    benchmark_group.add_argument("--guess", type=lambda s: s.upper())
    benchmark_group.add_argument("--size", type=int, default=5)
    benchmark_parser.add_argument("--solver", type=SolverType.from_str, default=SolverType.MINIMAX)
    benchmark_parser.add_argument("--depth", required=False, default=1, type=int)
    benchmark_parser.set_defaults(func=benchmark_performance)

    args = parser.parse_args()
    args.func(args)
