from typing import Tuple
import re

score_expr = re.compile(r"[0-2]+$")
word_expr = re.compile(r"^([A-Z]+)=([0-2]+)$")


def get_user_score(guess: str, size: int) -> Tuple[int, str]:

    is_valid = False

    while not is_valid:
        user_response = input(f"Enter observed score for {guess}:\n")
        sanitized_response = user_response.upper().replace(" ", "")
        (observed_score, guess, is_valid) = parse_response(guess, size, sanitized_response)

    return (observed_score, guess)


def parse_response(guess: str, size: int, response: str) -> Tuple[int, str, bool]:

    if len(response) == size and score_expr.match(response):
        observed_score = int(response)
        return (observed_score, guess, True)

    m = word_expr.match(response)

    if len(response) == (2 * size + 1) and response[size] == "=" and m:
        (user_guess, score) = m.groups()
        return (int(score), user_guess, True)

    return (-1, guess, False)
