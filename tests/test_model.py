import numpy as np
import pytest

from nerdle.scoring import Scorer
from nerdle.words import Word


@pytest.mark.parametrize(
    "solution,guess,expected",
    [
        ("SPEAR", "SPEAK", "22220"),
        ("SPEAR", "STRIP", "20101"),
        ("SPEAR", "SOLID", "20000"),
        ("SPEAR", "MAGIC", "01000"),
        ("SPEAR", "VAPID", "01100"),
        ("SPEAR", "STERN", "20210"),
        ("SPEAR", "SPEAR", "22222"),
        ("PERKY", "RAISE", "10001"),
        ("PERKY", "HERON", "02200"),
        ("PERKY", "PULLY", "20002"),
        ("PERKY", "PERRY", "22202"),
        ("PERKY", "PERKY", "22222"),
        ("PEACH", "CHART", "11200"),
        ("PEACH", "PEACH", "22222"),
        ("BASIC", "SPARE", "10100"),
        ("BASIC", "CLOUT", "10000"),
        ("BASIC", "FANGS", "02001"),
        ("BASIC", "DINKY", "01000"),
        ("BASIC", "MAGIC", "02022"),
        ("BASIC", "BASIC", "22222"),
        ("CRIMP", "APPLE", "01000"),
        ("AGATE", "SALAD", "01010"),
        ("AGATE", "ABACA", "20200"),
        ("AGATE", "BANAL", "01010"),
        ("AGATE", "AGATE", "22222"),
        ("GAMMA", "MUMMY", "00220"),
        ("GAMMA", "MIMIC", "10200"),
        ("GAMMA", "MAGIC", "12100"),
        ("GAMMA", "HAIRY", "02000"),
        ("GAMMA", "FUNDS", "00000"),
        ("GAMMA", "GAMMA", "22222"),
        ("ARGUE", "ERROR", "12000"),
        ("ARGUE", "TEARS", "01110"),
        ("ARGUE", "GRAPE", "12102"),
        ("ARGUE", "AGREE", "21102"),
        ("ARGUE", "ARGUE", "22222"),
    ],
)
def test_answer(solution: str, guess: str, expected: str) -> None:
    scorer = Scorer()
    score = scorer.score_word(Word(solution), Word(guess))
    assert int(np.base_repr(score, base=3)) == int(expected)
