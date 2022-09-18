from enum import Enum

from utils import get_char


class Choice(Enum):
    YES = 1
    EDIT = 3
    SKIP = 4


def get_selection() -> Choice:
    while True:
        print("Replace match with suggestion: Y(es, default)/e(dit)/s(kip)")
        char = get_char()
        match char:
            case "Y":
                return Choice.YES
            case "y":
                return Choice.YES
            case "\n":
                return Choice.YES
            case "e":
                return Choice.EDIT
            case "s":
                return Choice.SKIP
            case _:
                print("Invalid input! Try again.")
