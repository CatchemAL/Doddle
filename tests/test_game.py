from doddle.game import Game, SimultaneousGame
from doddle.words import Word, WordSeries

from .fake_dictionary import load_test_dictionary


class TestGame:
    def test_game_num_solutions(self) -> None:
        # Arrange
        soln = Word("STICK")
        dictionary = load_test_dictionary()

        sut = Game(dictionary.common_words, soln, [])

        # Act
        actual = sut.num_potential_solns

        # Assert
        assert actual == len(dictionary.common_words)

    def test_game_rounds(self) -> None:
        # Arrange
        soln = Word("STICK")
        dictionary = load_test_dictionary()
        expected = 0

        sut = Game(dictionary.common_words, soln, [])

        # Act
        actual = sut.rounds

        # Assert
        assert actual == expected

    def test_game_update(self) -> None:
        # Arrange
        soln = Word("STICK")
        dictionary = load_test_dictionary()

        sut = Game(dictionary.common_words, soln, [])

        # Act
        row = sut.update(1, soln, 242, WordSeries(["STICK"]))

        # Assert
        assert row.n == 1
        assert sut.is_solved


class TestSimultaneousGame:
    def test_game_rounds(self) -> None:
        # Arrange
        solns = [Word("STICK"), Word("TOXIC")]
        dictionary = load_test_dictionary()
        expected = 0

        sut = SimultaneousGame(dictionary.common_words, solns, [])

        # Act
        actual = sut.rounds

        # Assert
        assert actual == expected
