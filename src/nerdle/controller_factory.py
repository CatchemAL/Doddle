from .controllers import HideController, SolveController
from .views import HideView, SolveView


def create_solve_controller(size: int) -> SolveController:
    loader = WordLoader(size)
    view = SolveView(size)
    return SolveController(loader, view)


def create_hide_controller(size: int) -> HideController:
    loader = WordLoader(size)
    view = HideView(size)
    return HideController(loader, view)
