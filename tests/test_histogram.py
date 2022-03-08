from doddle.histogram import HistogramBuilder
from doddle.scoring import Scorer, from_ternary
from doddle.solver import MinimaxSolver
from doddle.words import Word, WordSeries


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
        guess_factory = MinimaxSolver._create_guess

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
