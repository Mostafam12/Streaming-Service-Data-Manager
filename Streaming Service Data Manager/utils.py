import os
import sqlite3
from typing import Callable, Dict, List


def run_from_list(message: str, choices: Dict[str, Callable], **kwargs):
    idx_chosen = get_choice_from_list(message, choices.keys())
    # items give us tuples of (name, function). we want to call the function
    return list(choices.items())[idx_chosen][1](**kwargs)


def get_choice_from_list(message, choices: List[str]):
    max_idx_choice_width = len(str(len(choices)))
    print(message or "Please choose one of the following options:")
    for idx, option in enumerate(choices):
        print(f' {idx + 1:>{max_idx_choice_width}}. {option}')
    return get_clamped_int(f"Enter an option: ", 1, len(choices)) - 1


def get_movie_title(*, message: str = None):
    return input(message or "Please enter a movie title: ")


def get_unique(message: str, table_name: str, column_name: str, cursor: sqlite3.Cursor, prompter=input, **kwargs):
    resp = prompter(message, **kwargs)
    while cursor.execute(f"SELECT 1 FROM {table_name} WHERE {column_name} LIKE ?", (resp,)).fetchone():
        print("Sorry, the value you entered was not unique (it should be)")
        resp = prompter(message, **kwargs)
    return resp


def get_string_with_restricted_length(message: str, length: int):
    def verifier(inp: str):
        assert len(inp.strip()) <= length, f"Your input should be under {length} chars long."
        return inp.strip()

    return get_input_of_arbitrary_type(message, verifier)


def get_clamped_int(message: str, low: int = None, high: int = None):
    def int_range_parser(inp: str):
        try:
            parsed = int(inp)
        except ValueError:
            raise AssertionError("Couldn't convert your input to an integer")
        if low is not None:
            assert parsed >= low, f"Your input must >= {low}"
        if high is not None:
            assert parsed <= high, f"Your input must <= {high}"
        return parsed

    return get_input_of_arbitrary_type(message or f"Enter a number between {low if low is not None else '-∞'}"
                                                  f" and {high if high is not None else '+∞'}: ", int_range_parser)


def get_yes_no(message, default: bool = True) -> bool:
    resp = input(message)
    if len(resp) == 0:
        return default
    if resp.lower() in ("yes", 'y'):
        return True
    if resp.lower() in ("no", "n"):
        return False
    return get_yes_no(message, default)

def pause(message: str) -> None:
    input(message)


def get_input_of_arbitrary_type(prompt: str, converter: Callable):
    try:
        return converter(input(prompt))
    except Exception as e:
        # technically, a stack overflow bug can occur here, but i don't care because by default stack limit is like 2k
        # ie, it would take 2k incorrect inputs to overflow the stack. at that point the user has deserved it in my book
        print(f"There was an error receiving input. {e.args[0]}")
        return get_input_of_arbitrary_type(prompt, converter)


def sqlite3_sort_concat_2_fields(*args):
    """
    Given args, concatenates the sorted string representation of them. This is useful when doing really specific
    stuff with GROUP BY, like editor q2. For example, given m1,m2 → m1m2. Given m2,m1 → m1m2. These 2 pairs containing the same
    data in different order will yield the same result.

    Args:
        *args: any number of arguments to sort and concatenate

    Returns:
        str
    """
    return "".join(map(str, sorted(args)))



# https://stackoverflow.com/questions/517970/how-to-clear-the-interpreter-console
def cls():
    """Cross-platform way to clear the screen"""
    os.system('cls' if os.name == 'nt' else 'clear')
