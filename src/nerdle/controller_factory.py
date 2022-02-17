from .controllers import BenchmarkController, HideController, RunController, SolveController
from .views import BenchmarkView, HideView, RunView, SolveView
from .words import WordLoader


def create_run_controller(size: int) -> RunController:
    loader = WordLoader(size)
    view = RunView(size)
    return RunController(loader, view)


def create_solve_controller(size: int) -> SolveController:
    loader = WordLoader(size)
    view = SolveView(size)
    return SolveController(loader, view)


def create_hide_controller(size: int) -> HideController:
    loader = WordLoader(size)
    view = HideView(size)
    return HideController(loader, view)


def create_benchmark_controller(size: int) -> BenchmarkController:
    loader = WordLoader(size)
    view = BenchmarkView()
    return BenchmarkController(loader, view)