from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Iterator

import numpy as np
from tqdm import tqdm

from doddle.enums import SolverType
from doddle.factory import create_models
from doddle.histogram import HistogramBuilder
from doddle.scoring import Scorer
from doddle.solver import EntropySolver
from doddle.words import Word, WordSeries


dictionary, scorer, histogram_builder, solver, _ = create_models(
    size=5, solver_type=SolverType.ENTROPY, lazy_eval=False
)


@dataclass
class TreeBuilder:
    scorer: Scorer
    histogram_builder: HistogramBuilder
    solver: EntropySolver
    permutation_limit: int = 8

    def build(self, potential_solns: WordSeries, opening_word: Word | str = "SALET") -> GuessNode:
        guess = Word(opening_word)
        node = GuessNode(guess)
        self.find_best_tree(potential_solns, node)
        return node

    def find_best_tree(self, potential_solns: WordSeries, parent: GuessNode, depth: int = 0) -> None:

        WIN_SCORE = self.scorer.perfect_score
        N_GUESSES = max(1, self.permutation_limit - 3 * depth)
        solns_by_score = self.histogram_builder.get_solns_by_score(potential_solns, parent.word)

        for score, inner_solns in tqdm(solns_by_score.items(), colour="green", disable=depth > 0):
            score_node = parent.add(score)
            if score == WIN_SCORE:
                continue
            if len(inner_solns) == 1:
                soln0 = inner_solns.iloc[0]
                score_node.add(soln0).add(WIN_SCORE)
                continue
            if len(inner_solns) == 2:
                soln0 = inner_solns.iloc[0]
                soln1 = inner_solns.iloc[1]
                score1 = self.scorer.score_word(soln1, soln0)
                score_node.add(soln0).add(WIN_SCORE)
                score_node.add(soln0).add(score1).add(soln1).add(WIN_SCORE)
                continue

            guesses = self.solver.all_guesses(all_words, inner_solns)
            best_guesses = sorted(guesses)[:N_GUESSES]
            naive_best_guess = best_guesses[0]

            if naive_best_guess.is_perfect_partition:
                guess_node = score_node.add(naive_best_guess.word)
                for soln in inner_solns:
                    score = self.scorer.score_word(soln, naive_best_guess.word)
                    score_node = guess_node.add(score)
                    if score != WIN_SCORE:
                        score_node.add(soln).add(WIN_SCORE)
                continue

            tree_size = 1_000_000_000
            best_node: GuessNode
            for guess in best_guesses:
                tmp_node = GuessNode(guess.word)
                self.find_best_tree(inner_solns, tmp_node, depth + 1)
                guess_count = tmp_node.guess_count()
                if guess_count < tree_size:
                    tree_size = guess_count
                    best_node = tmp_node

            guess_node = score_node.add(best_node.word)
            guess_node.children = best_node.children


class ScoreNode:

    __slots__ = ["score", "children"]

    def __init__(self, score: int) -> None:
        self.score: int = score
        self.children: list[GuessNode] = []

    def add(self, guess: Word) -> GuessNode:
        child_node = GuessNode(guess)
        self.children.append(child_node)
        return child_node

    def count(self) -> int:
        if self.children:
            return sum(child.count() for child in self.children)
        return 1

    def guess_count(self) -> int:
        return sum(child.guess_count() for child in self.children)

    def display(self, prefix: str = "") -> Iterator[str]:
        new_prefix = f"{prefix},{self.score}"
        if self.children:
            for child in self.children:
                yield from child.display(new_prefix)
        else:
            yield new_prefix


class GuessNode:
    __slots__ = ["word", "children"]

    def __init__(self, word: Word) -> None:
        self.word: Word = word
        self.children: list[ScoreNode] = []

    def add(self, score: int) -> ScoreNode:
        child_node = ScoreNode(score)
        self.children.append(child_node)
        return child_node

    def count(self) -> int:
        return sum(child.count() for child in self.children)

    def guess_count(self) -> int:
        return self.count() + sum(child.guess_count() for child in self.children)

    def csv(self, include_scores: bool = True) -> str:
        rows = list(self.display())
        if include_scores:
            return "\n".join(rows)

        filtered_rows = [",".join(row.split(",")[::2]) for row in rows]
        return "\n".join(filtered_rows)

    def display(self, prefix: str = "") -> list[str]:
        if prefix == "":
            new_prefix = self.word
        else:
            new_prefix = f"{prefix},{self.word}"

        for child in self.children:
            yield from child.display(new_prefix)


start_time = time.time()
all_words, common_words = dictionary.words


seed = Word("WAIST")
solns = ["DATUM", "GAMUT", "HABIT", "PATSY", "WAIST"]

seed = Word("TALON")
solns = ["BATON"]

seed = Word("TALON")
solns = ["TIDAL", "TUBAL"]

seed = Word("TALON")
solns = ["DATUM", "GAMUT", "HABIT", "PATSY", "WAIST"]

# seed = Word('WEDEL')
# solns = ['BONEY', 'GIVEN', 'GOOEY', 'HONEY', 'MONEY', 'HYMEN', 'NOSEY', 'PINEY', 'VIXEN']

# seed = Word("SALET")
# solns = common_words[:25_000]


# root.dump()

HOLY_GRAIL = 7920
subset = np.array([Word(word) for word in solns])
potential_solns = common_words[common_words.find_index(subset)]

for i in range(8, 11, 1):

    print(f"Permutations={i}")
    tree_builder = TreeBuilder(scorer, histogram_builder, solver, i)
    root = tree_builder.build(common_words, "SALET")
    c = root.count()
    gc = root.guess_count()
    print(f"Count={c:,}")
    print(f"Guess count={gc:,}")
    print(f"--- {(time.time() - start_time)} seconds ---")
    print()

    if gc <= HOLY_GRAIL:
        csv_content = root.csv(False)
        # print(csv_content)
        break
