from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Protocol, TypeVar


class Greeter(Protocol):
    def greet(self) -> None:
        ...

    def __lt__(self, other: Greeter) -> bool:
        ...


class Dog:
    def greet(self) -> None:
        print("Woof woof")

    def __lt__(self, other: Greeter) -> bool:
        return True


class Cow:
    def greet(self) -> None:
        print("Moo moo")

    def __lt__(self, other: Greeter) -> bool:
        return True


def call_greet(animal: Greeter) -> None:
    animal.greet()


def do_stuff(animal: Cow) -> None:
    call_greet(animal)


T = TypeVar("T", bound=Greeter)


class Box(Generic[T]):
    def __init__(self, content: T) -> None:
        self.content = content

    @property
    def value(self) -> T:
        return self.content


class CowBox(Box[Cow]):
    def __init__(self, content: Cow) -> None:
        super().__init__(content)


cow1 = Cow()
cow2 = Cow()
cow3 = Cow()

Box(cow1)  # OK, inferred type is Box[int]
Box[Cow](cow2)  # Also OK

s = Dog()
Box[Dog](s)  # Type error

sb = CowBox(cow3)
x = sb.content

cows: list[Greeter] = [cow1, cow2, cow3]
sorted_cows = sorted(cows)
