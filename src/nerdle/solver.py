from __future__ import annotations

import abc
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Set

from .scoring import Scorer


class Solver:
    def __init__(self, scorer: Scorer) -> None:
        self.scorer = scorer

    def prettify(self, solution: str, guess: str) -> None:
        score = self.scorer.score_word(solution, guess)
        size = len(solution)
        padded_score = f"{score}".zfill(size)
        message = f"{solution}, {guess}, {padded_score}"
        print(message)

    @abc.abstractmethod
    def get_best_guess(self, possible_solutions: Set[str], available_guesses: Set[str]) -> str:
        pass

    def get_possible_solutions_by_score(
        self, possible_solutions: Set[str], guess: str
    ) -> Dict[int, Set[str]]:
        possible_solutions_by_score = defaultdict(set)
        for solution in possible_solutions:
            score = self.scorer.score_word(solution, guess)
            possible_solutions_by_score[score].add(solution)

        return possible_solutions_by_score

    @staticmethod
    def seed(size: int) -> str:

        seed_by_size = {
            4: "OLEA",
            5: "RAISE",
            6: "TAILER",
            7: "TENAILS",
            8: "CENTRALS",
            9: "SECRETION",
        }

        return seed_by_size[size]


class MinimaxSolver(Solver):
    def get_best_guess(self, possible_solutions: Set[str], available_guesses: Set[str]) -> str:

        best_guess_to_date = Guess("N/A", 1_000_000, 1_000_000, {})

        for guess in available_guesses:
            possible_solutions_by_score = self.get_possible_solutions_by_score(
                possible_solutions, guess
            )
            new_guess = Guess.create(guess, possible_solutions_by_score)

            if new_guess.improves_upon(best_guess_to_date, possible_solutions):
                best_guess_to_date = new_guess

        return best_guess_to_date.word


class DeeperMinimaxSolver(Solver):
    N_BRANCH = 5

    def __init__(self, scorer: Scorer) -> None:
        self.minimax = MinimaxSolver(scorer)
        super().__init__(scorer)

    def get_best_guess(self, possible_solutions: Set[str], available_guesses: Set[str]) -> str:
        """Search one level deeper for guesses that have better worst case scenarios on the next round."""

        if len(possible_solutions) == 1:
            return possible_solutions.pop()

        best_guess_to_date = Guess("N/A", 1_000_000, 1_000_000, {})
        best_largest_bucket_to_date = 1_000_000

        bucket_guesses = {}

        for guess in available_guesses:
            possible_solutions_by_score = self.get_possible_solutions_by_score(
                possible_solutions, guess
            )
            new_guess = Guess.create(guess, possible_solutions_by_score)
            b_size = new_guess.size_of_largest_bucket

            if b_size not in bucket_guesses:
                bucket_guesses[b_size] = []

            bucket_guesses[b_size].append(new_guess)

        if 1 in bucket_guesses:
            # if any of the guesses would get us there next go, just choose one
            for guess in bucket_guesses[1]:
                if guess.improves_upon(best_guess_to_date, possible_solutions):
                    best_guess_to_date = guess
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
                    reverse=True
                )

                guess_largest_bucket = 0

                for score in solution_order:
                    # if there aren't many possible solutions then this can't result in a large bucket
                    if len(possible_solutions_by_score[score]) < guess_largest_bucket:
                        break

                    best_next_guess = self.minimax.get_best_guess(
                        possible_solutions_by_score[score], available_guesses
                    )
                    possible_next_solutions_by_score = self.get_possible_solutions_by_score(
                        possible_solutions_by_score[score], best_next_guess
                    )
                    size_of_largest_bucket = max(
                        len(group) for group in possible_next_solutions_by_score.values()
                    )
                    if size_of_largest_bucket > guess_largest_bucket:
                        guess_largest_bucket = size_of_largest_bucket

                if guess_largest_bucket == best_largest_bucket_to_date:
                    # if the new guess has as bad a largest bucket on the next round
                    if guess.improves_upon(best_guess_to_date, possible_solutions):
                        # assess it in this round and choose the better guess
                        best_guess_to_date = guess

                elif guess_largest_bucket < best_largest_bucket_to_date:
                    # if the new guess has a better largest bucket then it is the best guess
                    best_largest_bucket_to_date = guess_largest_bucket
                    best_guess_to_date = guess

        return best_guess_to_date.word


@dataclass
class Guess:

    word: str
    size_of_largest_bucket: int
    number_of_buckets: int
    possible_solutions_by_score: Dict[int, Set[str]]

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

    @staticmethod
    def create(guess: str, possible_solutions_by_score: Dict[int, Set[str]]) -> Guess:

        groups = possible_solutions_by_score.values()
        number_of_buckets = len(groups)
        size_of_largest_bucket = max(len(group) for group in groups)
        return Guess(guess, size_of_largest_bucket, number_of_buckets, possible_solutions_by_score)
