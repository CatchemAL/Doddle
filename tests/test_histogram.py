from unittest.mock import MagicMock, patch

import numpy as np

from doddle.guess import MinimaxGuess
from doddle.histogram import HistogramBuilder, ScoreMatrix, _populate_histogram
from doddle.scoring import Scorer, from_ternary
from doddle.words import Word, WordSeries
from tests.fake_dictionary import load_test_dictionary


class TestHistogramBuilder:
    def test_creates_expected_histogram(self) -> None:
        # Arrange
        guess = Word("THURL")

        expected = {
            "00000": ["SNAKE", "SPACE", "SPADE"],
            "00001": ["SCALE"],
            "00020": ["SCARE", "SNARE", "SPARE"],
            "02000": ["SHADE", "SHAKE", "SHAME", "SHAPE", "SHAVE"],
            "02001": ["SHALE"],
            "02020": ["SHARE", "SHARK"],
            "10000": ["SKATE", "STAGE", "STAVE"],
            "10001": ["SLATE", "STALE"],
        }

        words = [soln for solns in expected.values() for soln in solns]
        potential_solns = WordSeries(words)
        all_words = WordSeries(words + [guess.value])
        histogram_builder = HistogramBuilder(Scorer(), all_words, potential_solns)

        # Act
        histogram = histogram_builder.get_solns_by_score(potential_solns, guess)

        # Assert
        assert len(histogram) == len(expected)
        for ternary_score, bucketed_solns in expected.items():
            score = from_ternary(ternary_score)
            assert score in histogram

            actual_bucketed_solns = histogram[score]
            assert len(actual_bucketed_solns) == len(bucketed_solns)

            for soln in bucketed_solns:
                assert Word(soln) in actual_bucketed_solns

    def test_guess_stream(self) -> None:
        # Arrange
        guess = Word("THURL")

        expected = {
            "00000": ["SNAKE", "SPACE", "SPADE"],
            "00001": ["SCALE"],
            "00020": ["SCARE", "SNARE", "SPARE"],
            "02000": ["SHADE", "SHAKE", "SHAME", "SHAPE", "SHAVE"],
            "02001": ["SHALE"],
            "02020": ["SHARE", "SHARK"],
            "10000": ["SKATE", "STAGE", "STAVE"],
            "10001": ["SLATE", "STALE"],
        }

        words = [soln for solns in expected.values() for soln in solns]
        potential_solns = WordSeries(words)
        all_words = WordSeries(words + [guess.value])
        histogram_builder = HistogramBuilder(Scorer(), all_words, potential_solns)
        guess_factory = MinimaxGuess.from_histogram

        # Act
        guess_stream = histogram_builder.stream(all_words, potential_solns, guess_factory)
        guesses = list(guess_stream)
        best_guess = min(guesses)

        # Assert
        assert best_guess.word == guess
        assert best_guess.number_of_buckets == len(expected)
        assert best_guess.size_of_largest_bucket == len(expected["02000"])

        for g in guesses:
            assert g.is_common_word ^ (g.word == guess)

    def test_populate_histogram(self) -> None:
        # Arrange
        matrix = np.array(
            [
                [6, 0, 2, 0, 2, 4, 6],
                [6, 1, 3, 1, 3, 5, 6],
                [7, 2, 8, 2, 8, 3, 7],
                [1, 3, 9, 3, 9, 2, 1],
            ]
        )

        histogram = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        expected = np.array([0, 0, 2, 1, 0, 0, 0, 2, 2, 0])

        # Act
        is_potential_soln = _populate_histogram.py_func(matrix, 2, histogram)

        # Assert
        assert not is_potential_soln
        assert all(histogram == expected)

    def test_populate_histogram_with_potential_soln(self) -> None:
        # Arrange
        matrix = np.array(
            [
                [6, 0, 2, 0, 2, 4, 6],
                [6, 1, 3, 1, 3, 5, 6],
                [7, 2, 8, 2, 8, 3, 7],
                [1, 3, 9, 3, 9, 2, 1],
            ]
        )

        histogram = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        expected = np.array([0, 2, 1, 2, 0, 0, 0, 0, 0, 2])

        # Act
        is_potential_soln = _populate_histogram.py_func(matrix, 3, histogram)

        # Assert
        assert is_potential_soln
        assert all(histogram == expected)


class TestScoreMatrix:
    @patch.object(ScoreMatrix, "precompute")
    def test_create_without_lazy_eval_calls_precompute(self, patch_precompute: MagicMock) -> None:
        # Arrange
        scorer = Scorer()
        all_words, potential_solns = load_test_dictionary().words

        # Act
        _ = ScoreMatrix(scorer, all_words, potential_solns, lazy_eval=False)

        # Assert
        patch_precompute.assert_called_once()

    @patch.object(ScoreMatrix, "precompute")
    def test_create_with_lazy_eval_does_not_precompute(self, patch_precompute: MagicMock) -> None:
        # Arrange
        scorer = Scorer()
        all_words, potential_solns = load_test_dictionary().words

        # Act
        _ = ScoreMatrix(scorer, all_words, potential_solns, lazy_eval=True)

        # Assert
        patch_precompute.assert_not_called()
