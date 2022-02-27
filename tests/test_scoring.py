import pytest

from doddle.scoring import Scorer, to_ternary
from doddle.words import Word


class TestScorer:

    @pytest.mark.parametrize(
        "soln_str,guess_str,expected",
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
    def test_score_word(self, soln_str: str, guess_str: str, expected: str) -> None:
        # Arrange
        sut = Scorer()
        soln = Word(soln_str)
        guess = Word(guess_str)

        # Act
        score = sut.score_word(soln, guess)
        ternary = to_ternary(score, 5)

        # Assert
        assert ternary == expected

    def test_is_perfect_score(self) -> None:
        # Arrange
        sut = Scorer()
        agree = Word('AGREE')
        wrong = Word('WRONG')

        # Act
        agree_score = sut.score_word(agree, agree)
        wrong_score = sut.score_word(agree, wrong)
        
        # Assert
        assert sut.is_perfect_score(agree_score)
        assert not sut.is_perfect_score(wrong_score)