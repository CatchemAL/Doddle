from .controllers import BenchmarkController, HideController, SolveController
from .views import BenchmarkView, HideView, SolveView


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
