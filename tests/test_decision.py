import os
from pathlib import Path

from doddle.decision import GraphBuilder
from doddle.game import Game
from doddle.words import Word, WordSeries


def test_create_digraph() -> None:
    # Arrange
    expected = """
digraph Doddle {
\tgraph [dpi=60 fontname="Courier New" label="
Made with <3 using Doddle (https://pypi.org/project/doddle)" labelloc=b rankdir=LR]
\tnode [fontname="Courier New" shape=plaintext]
\tedge [arrowhead=vee color=cadetblue]
}"""

    builder = GraphBuilder([])

    # Act
    actual = builder.digraph.source

    # Asset
    assert actual.strip() == expected.strip()


def test_create_full_digraph() -> None:
    # Arrange
    directory = Path(os.path.dirname(__file__))
    path = directory / "expected_dot_code.gv"
    with open(path) as f:
        expected = f.read()

    series = WordSeries(["DUMMY"])

    soln1 = Word("TOWER")
    game1 = Game(series, soln1, [])
    game1.is_solved = True
    game1.scoreboard.add_row(1, soln1, Word("CRATE"), "01011", 35)
    game1.scoreboard.add_row(2, soln1, Word("TETRI"), "21010", 3)
    game1.scoreboard.add_row(3, soln1, Word("THREW"), "20121", 1)
    game1.scoreboard.add_row(4, soln1, Word("TOWER"), "22222", 1)

    soln2 = Word("LOWLY")
    game2 = Game(series, soln1, [])
    game2.is_solved = True
    game2.scoreboard.add_row(1, soln2, Word("CRATE"), "01011", 246)
    game2.scoreboard.add_row(2, soln2, Word("SOLID"), "21010", 6)
    game2.scoreboard.add_row(3, soln2, Word("WOOLY"), "20121", 1)
    game2.scoreboard.add_row(4, soln2, Word("LOWLY"), "22222", 1)

    soln3 = Word("SHAPE")
    game3 = Game(series, soln1, [])
    game3.is_solved = True
    game3.scoreboard.add_row(1, soln3, Word("CRATE"), "00202", 35)
    game3.scoreboard.add_row(2, soln3, Word("SLUNG"), "20000", 6)
    game3.scoreboard.add_row(3, soln3, Word("AMPED"), "10110", 1)
    game3.scoreboard.add_row(4, soln3, Word("LOWLY"), "22222", 1)

    builder = GraphBuilder([game1, game2, game3])

    # Act
    actual = builder.build().source

    # Asset
    assert actual.strip() == expected.strip()
