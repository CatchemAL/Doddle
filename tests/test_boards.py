

from doddle.boards import Keyboard


class TestKeyboard:
    def test_with_one_update(self) -> None:
        # Arrange
        sut = Keyboard()

        expected = {
            -1: 'BCDFGHIJLMOPQRTUVWXYZ',
            0: 'KN',
            1: 'AE',
            2: 'S',
        }

        # Act
        sut.update("SNAKE", '20101')

        # Assert
        for expected_digit, letters in expected.items():
            for char in letters:
                actual_digit = sut.digit_by_char[char]
                assert expected_digit == actual_digit

    def test_with_two_updates(self) -> None:
        # Arrange
        sut = Keyboard()

        expected = {
            -1: 'BCDFGHIJLOPQRUVWXZ',
            0: 'KMNTY',
            1: 'A',
            2: 'ES',
        }

        # Act
        sut.update("SNAKE", '20101')
        sut.update("MEATY", '02100')

        # Assert
        for expected_digit, letters in expected.items():
            for char in letters:
                actual_digit = sut.digit_by_char[char]
                assert expected_digit == actual_digit