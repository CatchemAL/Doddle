import os
from pathlib import Path

from doddle.boards import Scoreboard
from doddle.decision import GraphBuilder
from doddle.words import Word


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

    soln1 = Word("TOWER")
    scoreboard1 = Scoreboard()
    scoreboard1.add_row(1, soln1, Word("CRATE"), "01011", 35)
    scoreboard1.add_row(2, soln1, Word("TETRI"), "21010", 3)
    scoreboard1.add_row(3, soln1, Word("THREW"), "20121", 1)
    scoreboard1.add_row(4, soln1, Word("TOWER"), "22222", 1)

    soln2 = Word("LOWLY")
    scoreboard2 = Scoreboard()
    scoreboard2.add_row(1, soln2, Word("CRATE"), "01011", 246)
    scoreboard2.add_row(2, soln2, Word("SOLID"), "21010", 6)
    scoreboard2.add_row(3, soln2, Word("WOOLY"), "20121", 1)
    scoreboard2.add_row(4, soln2, Word("LOWLY"), "22222", 1)

    soln3 = Word("SHAPE")
    scoreboard3 = Scoreboard()
    scoreboard3.add_row(1, soln3, Word("CRATE"), "00202", 35)
    scoreboard3.add_row(2, soln3, Word("SLUNG"), "20000", 6)
    scoreboard3.add_row(3, soln3, Word("AMPED"), "10110", 1)
    scoreboard3.add_row(4, soln3, Word("LOWLY"), "22222", 1)

    builder = GraphBuilder([scoreboard1, scoreboard2, scoreboard3])

    # Act
    actual = builder.build().source

    # Asset
    assert actual.strip() == expected.strip()
