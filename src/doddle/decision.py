import graphviz
from doddle.factory import create_benchmarker
from doddle.scoring import to_ternary
from doddle.words import Word
from doddle.enums import SolverType

SIZE = 5

benchmarker = create_benchmarker(SIZE, solver_type=SolverType.ENTROPY)
games = benchmarker.run_benchmark([Word("CRATE")])
len(games)

allowed = {to_ternary(i, 5) for i in range(0, 2)}
# allowed = {'02011'}

filtered_scoreboards = [game.scoreboard for game in games if game.scoreboard.rows[0].score in allowed]
filtered_scoreboards

d = graphviz.Digraph(
    "G",
    filename="hello.gv",
    node_attr={"color": None, "shape": "plaintext", "fontname": "Courier New"},
    edge_attr={"color": "cadetblue", "arrowhead": "vee"},
)

d.graph_attr["rankdir"] = "LR"
d.graph_attr["dpi"] = "60"
d.graph_attr["label"] = "\nMade with <3 using Doddle (https://pypi.org/project/doddle)"
d.graph_attr["labelloc"] = "b"
d.graph_attr["fontname"] = "Courier New"

seen: set[tuple[str, str]] = set()


def add_edge(path1: str, path2: str) -> None:
    pair = path1, path2

    if pair in seen or path1 == "":
        return

    d.edge(path1, path2)
    seen.add(pair)


def add_node(path: str, label: str) -> None:
    pair = path, label

    if pair in seen:
        return

    d.node(path, label=label)
    seen.add(pair)


def add_node_html(path: str, label: str, ternary: str) -> None:
    pair = path, label

    if pair in seen:
        return

    color_by_score = ["#787c7e", "#c9b458", "#6aaa64"]
    cells = []
    for letter, tigit in zip(label, ternary):
        idx = int(tigit)
        color = color_by_score[idx]
        cell = f'                <td bgcolor="{color}" width="22" height="22"><font face="Helvetica" color="white">{letter}</font></td>'
        cells.append(cell)
    all_cells = "\n".join(cells)

    html = f"""<
        <table border="0" cellborder="0" cellspacing="2">
            <tr>
{all_cells}
            </tr>
        </table>>"""
    d.node(path, label=html)
    seen.add(pair)


for scoreboard in filtered_scoreboards:
    path = ""
    scores = ""
    prev_score_path = ""
    for row in scoreboard.rows:
        n = row.n
        guess = row.guess
        score = row.score

        guess_path = f"{scores}g{n}"
        add_node(guess_path, str(row.guess))
        add_edge(prev_score_path, guess_path)

        score_path = f"{scores}{score}"
        add_node_html(score_path, str(row.guess), row.score)
        add_edge(guess_path, score_path)

        scores += f"{score}-"
        prev_score_path = score_path

d.save("doddle_dot_file.gv")
# print(d.source)
d
