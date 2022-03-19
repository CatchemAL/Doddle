from unittest.mock import MagicMock, patch
from colorama import Fore

from doddle.boards import (
    EmojiScoreboardPrinter,
    HtmlScoreboardPrinter,
    Keyboard,
    KeyboardPrinter,
    Scoreboard,
    ScoreboardPrinter,
    ScoreboardRow,
)
from doddle.words import Word


class TestScoreboardRow:
    def test_row_repr(self) -> None:
        # Arrange
        soln = Word("SMOKE")
        guess = Word("GUESS")
        sut = ScoreboardRow(3, soln, guess, "00110", 123)
        expected = "n=3, soln=SMOKE, guess=GUESS, score=00110, num_left=123"

        # Act
        actual = repr(sut)

        # Assert
        assert actual == expected

    def test_row_to_dict(self) -> None:
        # Arrange
        soln = Word("SMOKE")
        guess = Word("GUESS")
        score = "00110"
        num_left = 123
        sut = ScoreboardRow(3, soln, guess, score, num_left)
        expected = {
            "n": 3,
            "Soln": str(soln),
            "Guess": str(guess),
            "Score": score,
            "Poss": num_left,
        }

        # Act
        actual = sut.to_dict(False)

        # Assert
        assert actual == expected


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

    def test_repr(self) -> None:
        # Arrange
        sut = Scoreboard()

        sut.add_row(1, Word("ULTRA"), Word("RAISE"), "01000", 117)
        sut.add_row(2, Word("ULTRA"), Word("URBAN"), "20010", 5)
        sut.add_row(3, Word("ULTRA"), Word("ULTRA"), "22222", 1)

        expected = "Soln=ULTRA (3 guesses)"

        # Act
        actual = repr(sut)

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
        3{keypad}2{keypad}

        ⬜🟨⬜⬜⬜ 🟩⬜⬜🟨⬜
        ⬜🟩🟨⬜🟨 🟩🟩🟩🟩🟩
        🟩🟩🟩🟩🟩 ⬛⬛⬛⬛⬛
        """
        expected = emojis.replace("        ", "")[1:-1]

        # Act
        actual = sut.emoji()

        # Assert
        assert actual == expected

    def test_html_repr(self) -> None:
        # Arrange
        sut = Scoreboard()

        sut.add_row(1, Word("ULTRA"), Word("RAISE"), "01000", 117)
        sut.add_row(1, Word("BLAST"), Word("URBAN"), "20010", 5)
        sut.add_row(2, Word("ULTRA"), Word("BLAST"), "02101", 1)
        sut.add_row(2, Word("BLAST"), Word("BLAST"), "22222", 1)
        sut.add_row(3, Word("ULTRA"), Word("ULTRA"), "22222", 1)

        expected = """
        <table>
        <thead>
          <tr>
            <th></th>
            <th>Soln</th>
            <th>Guess</th>
            <th>Score</th>
            <th>Poss</th>
          </tr>
        </thead>
        <tbody>
            <tr>
                <th>1</th>
                <td><tt>ULTRA</tt></td>
                <td><tt>RAISE</tt></td>
                <td>⬜🟨⬜⬜⬜</td>
                <td>117</td>
            </tr>
            <tr>
                <th>1</th>
                <td><tt>BLAST</tt></td>
                <td><tt>URBAN</tt></td>
                <td>🟩⬜⬜🟨⬜</td>
                <td>5</td>
            </tr>
                <tr>
                    <td colspan="5" class="divider"><hr /></td>
                </tr>
            <tr>
                <th>2</th>
                <td><tt>ULTRA</tt></td>
                <td><tt>BLAST</tt></td>
                <td>⬜🟩🟨⬜🟨</td>
                <td>1</td>
            </tr>
            <tr>
                <th>2</th>
                <td><tt>BLAST</tt></td>
                <td><tt>BLAST</tt></td>
                <td>🟩🟩🟩🟩🟩</td>
                <td></td>
            </tr>
                <tr>
                    <td colspan="5" class="divider"><hr /></td>
                </tr>
            <tr>
                <th>3</th>
                <td><tt>ULTRA</tt></td>
                <td><tt>ULTRA</tt></td>
                <td>🟩🟩🟩🟩🟩</td>
                <td></td>
            </tr>
        </tbody>
        </table>
        """

        # Act
        actual = sut._repr_html_()
        actual_sanitised = actual.strip().replace(" ", "")
        expected_sanitised = expected.strip().replace(" ", "")

        # Assert
        assert actual_sanitised == expected_sanitised


class TestScoreboardPrinter:
    def test_build_string(self) -> None:
        # Arrange
        scoreboard = Scoreboard()
        scoreboard.add_row(1, Word("ULTRA"), Word("RAISE"), "01000", 117)
        scoreboard.add_row(2, Word("ULTRA"), Word("URBAN"), "20010", 5)
        scoreboard.add_row(3, Word("ULTRA"), Word("ULTRA"), "22222", 1)

        sut = ScoreboardPrinter(size=5)

        emojis = f"""
        | # | Soln. | Guess | Score | Poss. |
        |---|-------|-------|-------|-------|
        | 1 | ULTRA | R{Fore.YELLOW}A{Fore.RESET}ISE | 0{Fore.YELLOW}1{Fore.RESET}000 |   117 |
        | 2 | ULTRA | {Fore.GREEN}U{Fore.RESET}RB{Fore.YELLOW}A{Fore.RESET}N | {Fore.GREEN}2{Fore.RESET}00{Fore.YELLOW}1{Fore.RESET}0 |     5 |
        | 3 | ULTRA | {Fore.GREEN}ULTRA{Fore.RESET} | {Fore.GREEN}22222{Fore.RESET} |       |
        """
        expected = emojis.replace("        ", "")[:-1]

        # Act
        scoreboard_str = sut.build_string(scoreboard)

        # Assert
        assert scoreboard_str == expected

    def test_print_last_round_if_empty(self) -> None:
        # Arrange
        sut = ScoreboardPrinter(size=5)
        scoreboard = Scoreboard()

        # Act
        expected = sut.print_last_round(scoreboard)

        # Assert
        assert expected is None


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


class TestHtmlScoreboardPrinter:
    @patch.object(HtmlScoreboardPrinter, "build_string")
    def test_print(self, mock_build_string: MagicMock) -> None:
        # Arrange
        sut = HtmlScoreboardPrinter()
        mocked_printout = "Mocked printout"
        mock_build_string.return_value = mocked_printout
        scoreboard = Scoreboard()

        # Act
        sut.print(scoreboard)

        # Assert
        mock_build_string.assert_called_once_with(scoreboard)


class TestEmojiScoreboardPrinter:
    @patch.object(EmojiScoreboardPrinter, "build_string")
    def test_print(self, mock_build_string: MagicMock) -> None:
        # Arrange
        sut = EmojiScoreboardPrinter()
        mocked_printout = "Mocked printout"
        mock_build_string.return_value = mocked_printout
        scoreboard = Scoreboard()

        # Act
        sut.print(scoreboard)

        # Assert
        mock_build_string.assert_called_once_with(scoreboard)

    def test_build_string(self) -> None:
        # Arrange
        sut = EmojiScoreboardPrinter()
        scoreboard = Scoreboard()
        expected = ""

        # Act
        actual = sut.build_string(scoreboard)

        # Assert
        assert actual == expected
