from doddle.decision import _create_digraph


def test_create_digraph() -> None:
    # Arrange
    expected = """
digraph Doddle {
\tgraph [dpi=60 fontname="Courier New" label="
Made with <3 using Doddle (https://pypi.org/project/doddle)" labelloc=b rankdir=LR]
\tnode [fontname="Courier New" shape=plaintext]
\tedge [arrowhead=vee color=cadetblue]
}"""

    # Act
    digraph = _create_digraph()

    # Asset
    print(digraph.source)
    assert digraph.source.strip() == expected.strip()
