from __future__ import annotations

import abc
from collections import defaultdict
from dataclasses import dataclass
from functools import cmp_to_key
from typing import Dict, Iterator, Set

from .scoring import Scorer


class Solver:
    def __init__(self, scorer: Scorer) -> None:
        self.scorer = scorer

    @abc.abstractmethod
    def get_best_guess(self, potential_solutions: Set[str], all_words: Set[str]) -> str:
        pass

    def get_solutions_by_score(self, potential_solns: Set[str], guess: str) -> Dict[int, Set[str]]:
        potential_solns_by_score = defaultdict(set)
        for soln in potential_solns:
            score = self.scorer.score_word(soln, guess)
            potential_solns_by_score[score].add(soln)

        return potential_solns_by_score

    @staticmethod
    def seed(size: int) -> str:

        seed_by_size = {
            4: "OLEA",
            5: "AESIR",
            6: "TAILER",
            7: "TENAILS",
            8: "CENTRALS",
            9: "SECRETION",
        }

        return seed_by_size[size]


class MinimaxSolver(Solver):
    def get_best_guess(self, potential_solutions: Set[str], all_words: Set[str]) -> Guess:
        guesses = self.all_guesses(potential_solutions, all_words)
        best_guess = min(guesses, key=Guess.comparer(potential_solutions))
        return best_guess

    def all_guesses(self, potential_solutions: Set[str], all_words: Set[str]) -> Iterator[Guess]:
        for word in all_words:
            solns_by_score = self.get_solutions_by_score(potential_solutions, word)
            guess = Guess.create(word, solns_by_score)
            yield guess


class DeepMinimaxSolver(MinimaxSolver):
    def __init__(self, inner_solver: Solver) -> None:
        super().__init__(inner_solver.scorer)
        self.solver = inner_solver

    def get_best_guess(self, potential_solutions: Set[str], all_words: Set[str]) -> Guess:

        N_BRANCH = 5

        guesses = self.all_guesses(potential_solutions, all_words)
        cmp_func = Guess.comparer(potential_solutions)
        best_guesses = sorted(guesses, key=cmp_func)[:N_BRANCH]

        nested_worst_best_guess_by_guess = {}

        for guess in best_guesses:
            solns_by_score = self.get_solutions_by_score(potential_solutions, guess.word)
            worst_outcomes = sorted(solns_by_score, key=lambda s: -len(solns_by_score[s]))
            nested_best_guesses = []
            for worst_outcome in worst_outcomes[:N_BRANCH]:
                nested_potential_solns = solns_by_score[worst_outcome]
                nested_best_guess = self.solver.get_best_guess(nested_potential_solns, all_words)
                nested_best_guesses.append(nested_best_guess)
            worst_best_guess = max(nested_best_guesses, key=cmp_func)
            nested_worst_best_guess_by_guess[guess.word] = worst_best_guess

        kvps = nested_worst_best_guess_by_guess.items()
        best_nested_worst_best_guess = min(nested_worst_best_guess_by_guess.values(), key=cmp_func)
        best_guess_str = next(key for key, value in kvps if value == best_nested_worst_best_guess)
        best_guess = next(guess for guess in best_guesses if guess.word == best_guess_str)
        return best_guess


class DeeperMinimaxSolver(Solver):
    N_BRANCH = 5

    def __init__(self, scorer: Scorer) -> None:
        self.minimax = MinimaxSolver(scorer)
        super().__init__(scorer)

    def get_best_guess(self, possible_solutions: Set[str], available_guesses: Set[str]) -> str:
        """Search one level deeper for guesses that have better next round worst case scenarios."""

        if len(possible_solutions) == 1:
            return possible_solutions.pop()

        best_guess = Guess("N/A", 1_000_000, 1_000_000, {})
        best_largest_bucket_to_date = 1_000_000

        bucket_guesses = {}

        for guess in available_guesses:
            possible_solutions_by_score = self.get_solutions_by_score(possible_solutions, guess)
            new_guess = Guess.create(guess, possible_solutions_by_score)
            b_size = new_guess.size_of_largest_bucket

            if b_size not in bucket_guesses:
                bucket_guesses[b_size] = []

            bucket_guesses[b_size].append(new_guess)

        if 1 in bucket_guesses:
            # if any of the guesses would get us there next go, just choose one
            for guess in bucket_guesses[1]:
                if guess.improves_upon(best_guess, possible_solutions):
                    best_guess = guess
        else:
            # only search the most plausible guesses
            search_guesses = []
            total_count = 0
            for b_size in sorted(bucket_guesses):
                search_guesses.extend(bucket_guesses[b_size])
                total_count += len(bucket_guesses[b_size])
                if (b_size == 1) or (total_count >= self.N_BRANCH):
                    break

            for guess in search_guesses:
                possible_solutions_by_score = guess.possible_solutions_by_score
                # loop through possible solutions in descending order of bucket size
                solution_order = sorted(
                    possible_solutions_by_score,
                    key=lambda x: len(possible_solutions_by_score[x]),
                    reverse=True,
                )

                guess_largest_bucket = 0

                for score in solution_order:
                    # if there aren't many possible solutions then skip
                    if len(possible_solutions_by_score[score]) < guess_largest_bucket:
                        break

                    best_next_guess = self.minimax.get_best_guess(
                        possible_solutions_by_score[score], available_guesses
                    ).word
                    possible_next_solutions_by_score = self.get_solutions_by_score(
                        possible_solutions_by_score[score], best_next_guess
                    )
                    size_of_largest_bucket = max(
                        len(group) for group in possible_next_solutions_by_score.values()
                    )
                    if size_of_largest_bucket > guess_largest_bucket:
                        guess_largest_bucket = size_of_largest_bucket

                if guess_largest_bucket == best_largest_bucket_to_date:
                    # if the new guess has as bad a largest bucket on the next round
                    if guess.improves_upon(best_guess, possible_solutions):
                        # assess it in this round and choose the better guess
                        best_guess = guess

                elif guess_largest_bucket < best_largest_bucket_to_date:
                    # if the new guess has a better largest bucket then it is the best guess
                    best_largest_bucket_to_date = guess_largest_bucket
                    best_guess = guess

        return best_guess.word


@dataclass
class Guess:

    word: str
    size_of_largest_bucket: int
    number_of_buckets: int

    def improves_upon(self, other: Guess, common_words: Set[str]) -> bool:

        if self.size_of_largest_bucket != other.size_of_largest_bucket:
            return self.size_of_largest_bucket < other.size_of_largest_bucket

        if self.word in common_words:
            if other.word not in common_words:
                return True
        else:
            if other.word in common_words:
                return False

        if self.number_of_buckets != other.number_of_buckets:
            return self.number_of_buckets > other.number_of_buckets

        return self.word < other.word

    def __str__(self) -> str:
        return self.word

    def __repr__(self) -> str:
        return f"{self.word=}, {self.size_of_largest_bucket=}, {self.number_of_buckets=}"

    @staticmethod
    def create(guess: str, possible_solutions_by_score: Dict[int, Set[str]]) -> Guess:

        groups = possible_solutions_by_score.values()
        number_of_buckets = len(groups)
        size_of_largest_bucket = max(len(group) for group in groups)
        return Guess(guess, size_of_largest_bucket, number_of_buckets)

    @staticmethod
    def comparer(potential_solutions: Set[str]):
        @cmp_to_key
        def cmp_items(guess1: Guess, guess2: Guess) -> int:
            if guess1.improves_upon(guess2, potential_solutions):
                return -1
            elif guess1 == guess2:
                return 0
            else:
                return 1

        return cmp_items
