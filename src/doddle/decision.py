from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from graphviz import Digraph  # type: ignore # pragma: no cover

from .game import Game

GREY = "#787c7e"
YELLOW = "#c9b458"
GREEN = "#6aaa64"


class GraphBuilder:
    def __init__(self, games: Iterable[Game]) -> None:
        self.color_by_score = [GREY, YELLOW, GREEN]
        self.seen: set[tuple[str, str]] = set()
        self.digraph = self._create_digraph()
        self.games = games

    def build(self) -> "Digraph":

        scoreboards = (game.scoreboard for game in self.games)
        for scoreboard in scoreboards:
            scores = ""
            prev_score_path = ""
            for row in scoreboard.rows:
                n = row.n
                score = row.score

                guess_path = f"{scores}g{n}"
                self.add_node(guess_path, str(row.guess))
                self.add_edge(prev_score_path, guess_path)

                score_path = f"{scores}{score}"
                self.add_node_html(score_path, str(row.guess), score)
                self.add_edge(guess_path, score_path)

                scores += f"{score}-"
                prev_score_path = score_path

        return self.digraph

    def add_edge(self, path1: str, path2: str) -> None:
        pair = path1, path2
        if path1 == "" or pair in self.seen:
            return

        self.digraph.edge(path1, path2)
        self.seen.add(pair)

    def add_node(self, path: str, label: str) -> None:
        pair = path, label
        if pair in self.seen:
            return

        self.digraph.node(path, label=label)
        self.seen.add(pair)

    def add_node_html(self, path: str, label: str, ternary: str) -> None:
        pair = path, label
        if pair in self.seen:
            return

        cells = []
        for letter, tigit in zip(label, ternary):
            idx = int(tigit)
            color = self.color_by_score[idx]
            cell = (
                f'                    <td bgcolor="{color}" width="22" height="22">'
                f'<font face="Helvetica" color="white">{letter}</font></td>'
            )
            cells.append(cell)
        all_cells = "\n".join(cells)

        html = f"""<
            <table border="0" cellborder="0" cellspacing="2">
                <tr>
{all_cells}
                </tr>
            </table>>"""
        self.digraph.node(path, label=html)
        self.seen.add(pair)

    @staticmethod
    def _create_digraph() -> "Digraph":

        from graphviz import Digraph  # type: ignore

        digraph = Digraph(
            "Doddle",
            filename="doddle.gv",
            node_attr={"color": None, "shape": "plaintext", "fontname": "Courier New"},
            edge_attr={"color": "cadetblue", "arrowhead": "vee"},
        )

        digraph.graph_attr["rankdir"] = "LR"
        digraph.graph_attr["dpi"] = "60"
        digraph.graph_attr["label"] = "\nMade with <3 using Doddle (https://pypi.org/project/doddle)"
        digraph.graph_attr["labelloc"] = "b"
        digraph.graph_attr["fontname"] = "Courier New"

        return digraph
