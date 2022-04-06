from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from tqdm import tqdm  # type: ignore

from .histogram import HistogramBuilder
from .scoring import Scorer
from .solver import EntropySolver
from .words import Dictionary, Word, WordSeries


@dataclass
class TreeBuilder:
    dictionary: Dictionary
    scorer: Scorer
    histogram_builder: HistogramBuilder
    solver: EntropySolver
    permutation_limit: int = 8

    def build(self, potential_solns: WordSeries, guess: Word | str) -> GuessNode:
        guess = Word(guess)
        node = GuessNode(guess)
        self.find_best_tree(potential_solns, node)
        return node

    def find_best_tree(self, potential_solns: WordSeries, parent: GuessNode, depth: int = 0) -> None:

        WIN_SCORE = self.scorer.perfect_score
        N_GUESSES = max(1, self.permutation_limit - 3 * depth)
        solns_by_score = self.histogram_builder.get_solns_by_score(potential_solns, parent.word)

        for score, inner_solns in tqdm(solns_by_score.items(), position=0, disable=depth > 0):
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

            guesses = self.solver.all_guesses(self.dictionary.all_words, inner_solns)
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

    def display(self, prefix: str = "") -> Iterator[str]:
        if prefix == "":
            new_prefix = str(self.word)
        else:
            new_prefix = f"{prefix},{self.word}"

        for child in self.children:
            yield from child.display(new_prefix)
