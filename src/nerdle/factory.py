from typing import Tuple

from .controllers import HideController, RunController, SolveController
from .scoring import Scorer
from .solver import Solver
from .views import HideView, RunView, SolveView
from .words import WordLoader


def create_run_controller(size: int) -> RunController:
    loader, solver = _create(size)
    view = RunView(size)
    return RunController(loader, solver, view)


def create_solve_controller(size: int) -> SolveController:
    loader, solver = _create(size)
    view = SolveView(size)
    return SolveController(loader, solver, view)


def create_hide_controller(size: int) -> HideController:
    loader, solver = _create(size)
    view = HideView(size)
    return HideController(loader, solver, view)


def _create(size: int) -> Tuple[WordLoader, Solver]:
    loader = WordLoader(size)
    scorer = Scorer(size)
    solver = Solver(scorer)
    return loader, solver
