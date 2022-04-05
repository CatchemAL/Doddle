from unittest.mock import MagicMock, patch

import numpy as np
from doddle import factory
from doddle.enums import SolverType

from doddle.tree import GuessNode, TreeBuilder
from doddle.words import Word
from tests.fake_dictionary import load_test_dictionary


class TestTreeBuilder:
    @patch.object(factory, "load_dictionary")
    def test_find_best_tree_with_win_guess(self, patch_load_dictionary: MagicMock) -> None:

        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()
        dictionary, scorer, histogram_builder, solver, _ = factory.create_models(
            5, solver_type=SolverType.ENTROPY
        )

        sut = TreeBuilder(dictionary, scorer, histogram_builder, solver)

        seed = Word("RETRO")
        solns = ["RETRO"]

        common_words = dictionary.common_words
        subset = np.array([Word(word) for word in solns])
        potential_solns = common_words[common_words.find_index(subset)]

        # Act
        guess_node = sut.build(potential_solns, seed)

        # Assert
        assert guess_node.csv() == "RETRO,242"

    @patch.object(factory, "load_dictionary")
    def test_find_best_tree_with_one_word(self, patch_load_dictionary: MagicMock) -> None:

        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()
        dictionary, scorer, histogram_builder, solver, _ = factory.create_models(
            5, solver_type=SolverType.ENTROPY
        )

        sut = TreeBuilder(dictionary, scorer, histogram_builder, solver)

        seed = Word("RETRO")
        solns = ["SNACK"]

        common_words = dictionary.common_words
        subset = np.array([Word(word) for word in solns])
        potential_solns = common_words[common_words.find_index(subset)]

        # Act
        guess_node = sut.build(potential_solns, seed)

        # Assert
        assert guess_node.csv() == "RETRO,0,SNACK,242"

    @patch.object(factory, "load_dictionary")
    def test_find_best_tree_with_two_left(self, patch_load_dictionary: MagicMock) -> None:

        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()
        dictionary, scorer, histogram_builder, solver, _ = factory.create_models(
            5, solver_type=SolverType.ENTROPY
        )

        sut = TreeBuilder(dictionary, scorer, histogram_builder, solver)

        seed = Word("VIVID")
        solns = ["FLAME", "FRAME"]

        common_words = dictionary.common_words
        subset = np.array([Word(word) for word in solns])
        potential_solns = common_words[common_words.find_index(subset)]

        # Act
        guess_node = sut.build(potential_solns, seed)

        # Assert
        assert guess_node.csv() == "VIVID,0,FLAME,242\nVIVID,0,FLAME,188,FRAME,242"

    @patch.object(factory, "load_dictionary")
    def test_find_best_tree_with_perfect_partition(self, patch_load_dictionary: MagicMock) -> None:

        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()
        dictionary, scorer, histogram_builder, solver, _ = factory.create_models(
            5, solver_type=SolverType.ENTROPY
        )

        sut = TreeBuilder(dictionary, scorer, histogram_builder, solver)

        seed = Word("VIVID")
        solns = ["FUNKY", "MUSKY", "ROOMY"]

        common_words = dictionary.common_words
        subset = np.array([Word(word) for word in solns])
        potential_solns = common_words[common_words.find_index(subset)]

        expected = """
VIVID,0,FUNKY,242
VIVID,0,FUNKY,62,MUSKY,242
VIVID,0,FUNKY,2,ROOMY,242
"""

        # Act
        guess_node = sut.build(potential_solns, seed)

        # Assert
        assert guess_node.csv() == expected.strip()

    @patch.object(factory, "load_dictionary")
    def test_find_best_tree_with_recursive_solve(self, patch_load_dictionary: MagicMock) -> None:

        # Arrange
        patch_load_dictionary.return_value = load_test_dictionary()
        dictionary, scorer, histogram_builder, solver, _ = factory.create_models(
            5, solver_type=SolverType.ENTROPY
        )

        sut = TreeBuilder(dictionary, scorer, histogram_builder, solver, 2)

        seed = Word("VIVID")
        common_words = dictionary.common_words

        # Act
        guess_node = sut.build(common_words, seed)

        # Assert
        assert guess_node.count() == len(common_words)
        assert guess_node.guess_count() == 282


class TestGuessNode:
    def test_add_score_node(self) -> None:
        # Arrange
        root = Word("ROOT0")
        node1 = Word("NODE1")
        node2 = Word("NODE2")
        node3 = Word("NODE3")
        sut = GuessNode(root)

        # Act
        sut.add(242)
        sut.add(101).add(node1).add(242)
        sut.add(205).add(node2).add(242)
        sut.add(205).add(node2).add(100).add(node3).add(242)

        # Assert
        assert len(sut.children) == 4
        assert sut.count() == 4
        assert sut.guess_count() == 8

    def test_csv_with_scores(self) -> None:
        # Arrange
        root = Word("ROOT0")
        node1 = Word("NODE1")
        node2 = Word("NODE2")
        node3 = Word("NODE3")
        sut = GuessNode(root)

        expected = """
ROOT0,242
ROOT0,101,NODE1,242
ROOT0,205,NODE2,242
ROOT0,205,NODE2,100,NODE3,242
        """

        sut.add(242)
        sut.add(101).add(node1).add(242)
        sut.add(205).add(node2).add(242)
        sut.add(205).add(node2).add(100).add(node3).add(242)

        # Act
        actual = sut.csv()

        # Assert
        assert actual == expected.strip()

    def test_csv_without_scores(self) -> None:
        # Arrange
        root = Word("ROOT0")
        node1 = Word("NODE1")
        node2 = Word("NODE2")
        node3 = Word("NODE3")
        sut = GuessNode(root)

        expected = """
ROOT0
ROOT0,NODE1
ROOT0,NODE2
ROOT0,NODE2,NODE3
        """

        sut.add(242)
        sut.add(101).add(node1).add(242)
        sut.add(205).add(node2).add(242)
        sut.add(205).add(node2).add(100).add(node3).add(242)

        # Act
        actual = sut.csv(False)

        # Assert
        assert actual == expected.strip()
