from colorama import Fore

from doddle.boards import Keyboard, KeyboardPrinter, Scoreboard
from doddle.words import Word


class TestScoreboard:
    def test_emoji_repr(self) -> None:
        # Arrange
        sut = Scoreboard()

        sut.add_row(1, Word("ULTRA"), Word("RAISE"), "01000", 117)
        sut.add_row(2, Word("ULTRA"), Word("URBAN"), "20010", 5)
        sut.add_row(3, Word("ULTRA"), Word("ULTRA"), "22222", 1)

        emojis = """
        Doddle 3/6

        ⬜🟨⬜⬜⬜
        🟩⬜⬜🟨⬜
        🟩🟩🟩🟩🟩
        """
        expected = emojis.replace("        ", "")[1:-1]

        # Act
        actual = sut.emoji()

        # Assert
        assert actual == expected

    def test_emoji_repr(self) -> None:
        # Arrange
        sut = Scoreboard()

        sut.add_row(1, Word("ULTRA"), Word("RAISE"), "01000", 117)
        sut.add_row(1, Word("BLAST"), Word("URBAN"), "20010", 5)
        sut.add_row(2, Word("ULTRA"), Word("BLAST"), "02101", 1)
        sut.add_row(2, Word("BLAST"), Word("BLAST"), "22222", 1)
        sut.add_row(3, Word("ULTRA"), Word("ULTRA"), "22222", 1)

        keypad = "\ufe0f\u20e3"

        emojis = f"""
        Doddle 3/7
        3{keypad}
        2{keypad}

        ⬜🟨⬜⬜⬜
        ⬜🟩🟨⬜🟨
        🟩🟩🟩🟩🟩

        🟩⬜⬜🟨⬜
        🟩🟩🟩🟩🟩
        """
        expected = emojis.replace("        ", "")[1:-1]

        # Act
        actual = sut.emoji()

        # Assert
        assert actual == expected


class TestKeyboard:
    def test_with_one_update(self) -> None:
        # Arrange
        sut = Keyboard()

        expected = {
            -1: "BCDFGHIJLMOPQRTUVWXYZ",
            0: "KN",
            1: "AE",
            2: "S",
        }

        # Act
        sut.update("SNAKE", "20101")

        # Assert
        for expected_digit, letters in expected.items():
            for char in letters:
                actual_digit = sut.digit_by_char[char]
                assert expected_digit == actual_digit

    def test_with_two_updates(self) -> None:
        # Arrange
        sut = Keyboard()

        expected = {
            -1: "BCDFGHIJLOPQRUVWXZ",
            0: "KMNTY",
            1: "A",
            2: "ES",
        }

        # Act
        sut.update("SNAKE", "20101")
        sut.update("MEATY", "02100")

        # Assert
        for expected_digit, letters in expected.items():
            for char in letters:
                actual_digit = sut.digit_by_char[char]
                assert expected_digit == actual_digit


class TestKeyboardPrinter:
    def test_printer_string(self) -> None:

        # Arrange
        keyboard = Keyboard()
        sut = KeyboardPrinter()
        keyboard.update("SNAKE", "20101")

        expected = f"""
    Q  W  {Fore.YELLOW}E  {Fore.RESET}R  T  Y  U  I  O  P
     {Fore.YELLOW}A  {Fore.GREEN}S  {Fore.RESET}D  F  G  H  J  {Fore.LIGHTBLACK_EX}K  {Fore.RESET}L
      Z  X  C  V  B  {Fore.LIGHTBLACK_EX}N  {Fore.RESET}M
      """

        # Act
        actual = sut.build_string(keyboard)

        # Assert
        assert expected == actual
