from doddle.histogram import HistogramBuilder
from doddle.scoring import Scorer
from doddle.solver import DeepEntropySolver, DeepMinimaxSolver, EntropySolver, MinimaxSolver
from doddle.words import Word, WordSeries


class TestMinimaxSolver:
    def test_get_best_guess(self) -> None:
        # Arrange
        remaining = (
            ["SNAKE", "SPACE", "SPADE", "SCALE", "SCARE", "SNARE", "SPARE"]
            + ["SHADE", "SHAKE", "SHAME", "SHAPE", "SHAVE", "SHALE"]
            + ["SHARE", "SHARK", "SKATE", "STAGE", "STAVE", "SLATE", "STALE"]
        )

        words = ["BLAST", "TRASH", "CARRY", "NYMPH", "PLANT"] + remaining
        potential_solns = WordSeries(remaining)
        all_words = WordSeries(words)
        histogram_builder = HistogramBuilder(Scorer(), all_words, potential_solns)
        sut = MinimaxSolver(histogram_builder)

        # Act
        best_guess = sut.get_best_guess(all_words, potential_solns)

        # Assert
        assert best_guess.word == Word("TRASH")


class TestDeepMinimaxSolver:
    def test_get_best_guess(self) -> None:
        # Arrange
        remaining = (
            ["SNAKE", "SPACE", "SPADE", "SCALE", "SCARE", "SNARE", "SPARE"]
            + ["SHADE", "SHAKE", "SHAME", "SHAPE", "SHAVE", "SHALE"]
            + ["SHARE", "SHARK", "SKATE", "STAGE", "STAVE", "SLATE", "STALE"]
        )

        words = ["BLAST", "TRASH", "CARRY", "NYMPH", "PLANT"] + remaining
        potential_solns = WordSeries(remaining)
        all_words = WordSeries(words)
        histogram_builder = HistogramBuilder(Scorer(), all_words, potential_solns)
        inner_solver = MinimaxSolver(histogram_builder)
        sut = DeepMinimaxSolver(histogram_builder, inner_solver)

        # Act
        best_guess = sut.get_best_guess(all_words, potential_solns)

        # Assert
        assert best_guess.word == Word("SHARK")

    def test_get_best_guess_with_only_two_solns(self) -> None:
        # Arrange
        remaining = ["SNAKE", "SPACE"]
        expected = Word("SNAKE")

        words = ["BLAST", "TRASH", "CARRY", "NYMPH", "PLANT"] + remaining
        potential_solns = WordSeries(remaining)
        all_words = WordSeries(words)
        histogram_builder = HistogramBuilder(Scorer(), all_words, potential_solns)
        inner_solver = MinimaxSolver(histogram_builder)
        sut = DeepMinimaxSolver(histogram_builder, inner_solver)

        # Act
        actual = sut.get_best_guess(all_words, potential_solns)

        # Assert
        assert actual.word == expected

    def test_get_best_guess_when_perfectly_partitioned(self) -> None:
        # Arrange
        remaining = ["SNAKE", "SPACE", "SHAPE"]
        expected = Word("SHAPE")

        words = ["BLAST", "TRASH", "CARRY", "NYMPH", "PLANT"] + remaining
        potential_solns = WordSeries(remaining)
        all_words = WordSeries(words)
        histogram_builder = HistogramBuilder(Scorer(), all_words, potential_solns)
        inner_solver = MinimaxSolver(histogram_builder)
        sut = DeepMinimaxSolver(histogram_builder, inner_solver)

        # Act
        actual = sut.get_best_guess(all_words, potential_solns)

        # Assert
        assert actual.word == expected
        assert actual.size_of_largest_bucket == 0


class TestEntropySolver:
    def test_get_best_guess(self) -> None:
        # Arrange
        remaining = (
            ["SNAKE", "SPACE", "SPADE", "SCALE", "SCARE", "SNARE", "SPARE"]
            + ["SHADE", "SHAKE", "SHAME", "SHAPE", "SHAVE", "SHALE"]
            + ["SHARE", "SHARK", "SKATE", "STAGE", "STAVE", "SLATE", "STALE"]
        )

        words = ["BLAST", "TRASH", "CARRY", "NYMPH", "PLANT"] + remaining
        potential_solns = WordSeries(remaining)
        all_words = WordSeries(words)
        histogram_builder = HistogramBuilder(Scorer(), all_words, potential_solns)
        sut = EntropySolver(histogram_builder)

        # Act
        best_guess = sut.get_best_guess(all_words, potential_solns)

        # Assert
        assert best_guess.word == Word("PLANT")


class TestDeepEntropySolver:
    def test_get_best_guess(self) -> None:
        # Arrange
        remaining = (
            ["SNAKE", "SPACE", "SPADE", "SCALE", "SCARE", "SNARE", "SPARE"]
            + ["SHADE", "SHAKE", "SHAME", "SHAPE", "SHAVE", "SHALE"]
            + ["SHARE", "SHARK", "SKATE", "STAGE", "STAVE", "SLATE", "STALE"]
        )

        words = ["BLAST", "TRASH", "CARRY", "NYMPH", "PLANT"] + remaining
        potential_solns = WordSeries(remaining)
        all_words = WordSeries(words)
        histogram_builder = HistogramBuilder(Scorer(), all_words, potential_solns)
        inner_solver = EntropySolver(histogram_builder)
        sut = DeepEntropySolver(histogram_builder, inner_solver)

        # Act
        best_guess = sut.get_best_guess(all_words, potential_solns)

        # Assert
        assert best_guess.word == Word("NYMPH")

    def test_get_best_guess_with_only_two_solns(self) -> None:
        # Arrange
        remaining = ["SNAKE", "SPACE"]
        expected = Word("SNAKE")

        words = ["BLAST", "TRASH", "CARRY", "NYMPH", "PLANT"] + remaining
        potential_solns = WordSeries(remaining)
        all_words = WordSeries(words)
        histogram_builder = HistogramBuilder(Scorer(), all_words, potential_solns)
        inner_solver = EntropySolver(histogram_builder)
        sut = DeepEntropySolver(histogram_builder, inner_solver)

        # Act
        actual = sut.get_best_guess(all_words, potential_solns)

        # Assert
        assert actual.word == expected

    def test_get_best_guess_when_perfectly_partitioned(self) -> None:
        # Arrange
        remaining = ["SNAKE", "SPACE", "SHAPE"]
        expected = Word("SHAPE")

        words = ["BLAST", "TRASH", "CARRY", "NYMPH", "PLANT"] + remaining
        potential_solns = WordSeries(remaining)
        all_words = WordSeries(words)
        histogram_builder = HistogramBuilder(Scorer(), all_words, potential_solns)
        inner_solver = EntropySolver(histogram_builder)
        sut = DeepEntropySolver(histogram_builder, inner_solver)

        # Act
        actual = sut.get_best_guess(all_words, potential_solns)

        # Assert
        assert actual.word == expected
        assert actual.entropy == float("inf")
