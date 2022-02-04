import json
from pathlib import Path
from typing import Set


class WordLoader:
    def __init__(self, size: int) -> None:
        self.size = size

        if size == 5:
            # Use the official Wordle list for the real game
            self.all_words = self.load_from_file("dictionary-full-official.json")
            self.common_words = self.load_from_file("dictionary-answers-official.json")
        else:
            self.all_words = self.load_from_file("dictionary-full.json")
            self.common_words = self.load_from_file("dictionary-answers.json")

    def load_from_file(self, file_name: str) -> Set[str]:
        path = Path(__file__).parent.absolute()
        SUB_FOLDER = 'dictionaries'
        with open(path / SUB_FOLDER / file_name) as file:
            word_list = json.load(file)
            return {word.upper() for word in word_list if len(word) == self.size}
