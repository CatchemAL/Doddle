from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from graphviz import Digraph  # type: ignore # pragma: no cover

from .game import Game


def digraph(games: Iterable[Game]) -> "Digraph":

    GREY = "#787c7e"
    YELLOW = "#c9b458"
    GREEN = "#6aaa64"

    color_by_score = [GREY, YELLOW, GREEN]
    seen: set[tuple[str, str]] = set()
    digraph = _create_digraph()

    def add_edge(path1: str, path2: str) -> None:
        pair = path1, path2
        if pair in seen or path1 == "":
            return

        digraph.edge(path1, path2)
        seen.add(pair)

    def add_node(path: str, label: str) -> None:
        pair = path, label
        if pair in seen:
            return

        digraph.node(path, label=label)
        seen.add(pair)

    def add_node_html(path: str, label: str, ternary: str) -> None:
        pair = path, label
        if pair in seen:
            return

        cells = []
        for letter, tigit in zip(label, ternary):
            idx = int(tigit)
            color = color_by_score[idx]
            cell = (
                f'                <td bgcolor="{color}" width="22" height="22">'
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
        digraph.node(path, label=html)
        seen.add(pair)

    scoreboards = (game.scoreboard for game in games)
    # worst_solve = max(scoreboard.rows[-1].n for scoreboard in scoreboards)
    # scores = [0] * worst_solve

    # def rank(scoreboard: Scoreboard) -> tuple[int, ...]:
    #     for i, row in enumerate(scoreboard.rows):
    #         scores[i] = from_ternary(row.score)
    #     return tuple(scores)

    # sorted_scoreboards = sorted(scoreboards, key=rank, reverse=True)
    # mid_point = len(scoreboards) // 2
    # zipped = zip(sorted_scoreboards[:mid_point], sorted_scoreboards[mid_point:])
    # boards = [board for pair in zipped for board in pair]
    # if len(boards) < len(sorted_scoreboards):
    #     boards.append(sorted_scoreboards[-1])

    # top = []
    # bottom = []
    # grps2 = groupby(scoreboards, key=lambda sb: sb.rows[0].score)
    # grps = [list(v) for _, v in grps2]
    # is_top = True
    # for grp in sorted(grps, key=len, reverse=True):
    #     is_top = not is_top
    #     if is_top:
    #         top.extend(grp)
    #     else:
    #         bottom.extend(grp)

    # bottom.reverse()
    # boards = top + bottom

    for scoreboard in scoreboards:
        scores = ""
        prev_score_path = ""
        for row in scoreboard.rows:
            n = row.n
            score = row.score

            guess_path = f"{scores}g{n}"
            add_node(guess_path, str(row.guess))
            add_edge(prev_score_path, guess_path)

            score_path = f"{scores}{score}"
            add_node_html(score_path, str(row.guess), score)
            add_edge(guess_path, score_path)

            scores += f"{score}-"
            prev_score_path = score_path

    return digraph


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
