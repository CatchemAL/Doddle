import numpy as np
from collections import defaultdict
from .scoring import Scorer

def seed(size: int) -> str:
    if size == 5:
        return 'RAISE'
    else:
        return 'TAILER'

class Solver:

    def __init__(self, scorer: Scorer) -> None:
        self.scorer = scorer

    def prettify(self, solution: str, guess: str):
        score = self.scorer.score_word(solution, guess)
        size = len(solution)
        padded_score = f'{score}'.zfill(size)
        message = f'{solution}, {guess}, {padded_score}'
        print(message)

    def get_best_guess(self, possible_solutions, available_guesses):

        largest_bucket_to_date = 1_000_000
        best_guess = ''

        if len(possible_solutions) == 1:
            return possible_solutions[0]

        for guess in available_guesses:
            possible_solutions_by_score = self.get_possible_solutions_by_score(possible_solutions, guess)
            groups = possible_solutions_by_score.values()
            number_of_buckets = len(groups)
            largest_bucket = max(len(group) for group in groups)

            if largest_bucket <= largest_bucket_to_date:
                if largest_bucket == largest_bucket_to_date:
                    if is_common_word and guess not in possible_solutions:
                        # print(f'Skipping because {guess} is less common than {best_guess}')
                        continue
                    elif number_of_buckets_to_date > number_of_buckets:
                        # print(f'Skipping because {guess} fragments the results less than {best_guess}')
                        continue

                message = '' if (guess in possible_solutions) else 'not '
                # print(f'{guess} has a min-max of {largest_bucket}, produces {len(groups)} buckets and is {message}a common word.')
                best_guess = guess
                largest_bucket_to_date = largest_bucket
                number_of_buckets_to_date = number_of_buckets
                is_common_word = guess in possible_solutions
        
        return best_guess

    def get_possible_solutions_by_score(self, possible_solutions, guess):
        possible_solutions_by_score = defaultdict(lambda: [])
        for solution in possible_solutions:
            score = self.scorer.score_word(solution, guess)
            possible_solutions_by_score[score].append(solution)

        return possible_solutions_by_score