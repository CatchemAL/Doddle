from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field

from doddle.exceptions import FailedToFindASolutionError
from doddle.game import Game, SimultaneousGame
from doddle.guess import Guess, MinimaxGuess, EntropyGuess
from doddle.histogram import HistogramBuilder
from doddle.scoring import Scorer
from doddle.solver import Solver, MinimaxSolver, EntropySolver
from doddle.views import RunReporter
from doddle.words import Dictionary, Word, WordSeries
from doddle.factory import create_models
from doddle.enums import SolverType

dictionary, scorer, histogram_builder, solver, _ = create_models(
    size=5, solver_type=SolverType.ENTROPY, lazy_eval=False
)

import time

start_time = time.time()


@dataclass
class TreeSize:
    VALUE: int = 1


tz = TreeSize()


@dataclass
class ScoreNode:
    score: int
    children: list[GuessNode] = field(default_factory=list)

    def add(self, guess: Word) -> GuessNode:
        child_node = GuessNode(guess)
        self.children.append(child_node)
        return child_node

    def count(self) -> int:
        if self.score == WIN_SCORE:
            return 1
        return sum(child.count() for child in self.children)

    def guess_count(self) -> int:
        return sum(child.guess_count() for child in self.children)

    def display(self, prefix: str = "") -> list[str]:
        if self.score == WIN_SCORE:
            yield f"{prefix},{self.score}"

        new_prefix = f"{prefix},{self.score}"
        for child in self.children:
            yield from child.display(new_prefix)


@dataclass
class GuessNode:
    word: Word
    children: list[ScoreNode] = field(default_factory=list)

    def add(self, score: int) -> ScoreNode:
        child_node = ScoreNode(score)
        self.children.append(child_node)
        return child_node

    def count(self) -> int:
        return sum(child.count() for child in self.children)

    def guess_count(self) -> int:
        return self.count() + sum(child.guess_count() for child in self.children)

    def dump(self) -> None:
        lines = "\n".join(list(self.display()))
        print(lines)

    def display(self, prefix: str = "") -> list[str]:
        if prefix == "":
            new_prefix = self.word
        else:
            new_prefix = f"{prefix},{self.word}"

        for child in self.children:
            yield from child.display(new_prefix)


all_words, common_words = dictionary.words
WIN_SCORE = 242
HOLY_GRAIL = 7920


def find_best_tree(potential_solns: WordSeries, parent: GuessNode) -> GuessNode:

    N_GUESSES = tz.VALUE

    solns_by_score = histogram_builder.get_solns_by_score(potential_solns, parent.word)

    for score, inner_solns in solns_by_score.items():
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
            score1 = scorer.score_word(soln1, soln0)
            score_node.add(soln0).add(WIN_SCORE)
            score_node.add(soln0).add(score1).add(soln1).add(WIN_SCORE)
            continue

        guesses = solver.all_guesses(all_words, inner_solns)
        best_guesses = sorted(guesses)[:N_GUESSES]
        naive_best_guess = best_guesses[0]

        if naive_best_guess.num_buckets == len(inner_solns):
            guess_node = score_node.add(naive_best_guess.word)
            for soln in inner_solns:
                score = scorer.score_word(soln, naive_best_guess.word)
                score_node = guess_node.add(score)
                if score != WIN_SCORE:
                    score_node.add(soln).add(WIN_SCORE)
            continue

        tree_size = 1_000_000_000
        best_node: GuessNode
        best_guess: Word
        for guess in best_guesses:
            tmp_node = GuessNode(guess.word)
            find_best_tree(inner_solns, tmp_node)
            guess_count = tmp_node.guess_count()
            if guess_count < tree_size:
                best_guess = guess.word
                best_node = tmp_node
                tree_size = guess_count

        guess_node = score_node.add(best_guess)
        guess_node.children = best_node.children


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

seed = Word("SALET")
solns = common_words[:25_000]


subset = np.array([Word(word) for word in solns])
potential_solns = common_words[common_words.find_index(subset)]

for i in range(1, 50):
    tz.VALUE = i
    node = GuessNode(seed)
    print()
    print(f"Scanning with {i} branches")
    find_best_tree(potential_solns, node)
    c = node.count()
    gc = node.guess_count()
    print(f"Count={c:,}")
    print(f"Guess count={gc:,}")
    print("--- %s seconds ---" % (time.time() - start_time))
    if gc <= HOLY_GRAIL:
        node.dump()
        break
