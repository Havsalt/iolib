"""
IO library inspired by the builtin function 'input'
* selection
* input_write
* input_hidden

Also contains decorator 'overload'
- Used to define a function multiple times
- Distinguishes by looking at argument types
- Return types does not make it distinguisable 
"""

import msvcrt
import sys
from typing import Any


__all__ = [
    "selection",
    "input_write",
    "input_hidden",
    "OverloadUnmatched",
    "overload"
]
__author__ = "FloatingInt"


def selection(*options, prompt: Any = None, capitalize: bool = False, deco: str = " ") -> Any:
    """
    Navigate up or down to select an option.
    Use PgUp/PgDown to navigate between options.

    Parameters
    ----------
    *options : `optional keyword arguments`
        - Options to choose from (at least 1 is required)
    prompt : `str`, `optional`, default: ``
        - Text displayed above the options
    capitalize : `bool`, `optional`, default: `False`
        - Capitalizes the first character in option
    deco : `str`, `optional`, default: `" "`
        - Capitalizes the first character in each option
    """

    string = ""
    size = len(options)
    curr = 0

    if not prompt == None:
        # display prompt
        sys.stdout.write(str(prompt) + "\n")

    # convert to string and capitalize if 'capitalize' == True
    lines = [deco + str(option).capitalize() if capitalize else deco + str(option)
             for option in options]
    string = "\n".join(lines)
    # display
    sys.stdout.write(string)

    # move cursor up to first option (exludeing prompt)
    sys.stdout.write("\r")
    for _ in range(size - 1):
        sys.stdout.write("\u001b[1A")

    # local contants
    UP = b"H"
    DOWN = b"P"
    ENTER = b"\r"

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == ENTER:
                # cleanup
                sys.stdout.write("\r" + "\n" * (size - curr))
                # index options
                return options[curr]

            elif key == UP:
                if curr > 0:
                    sys.stdout.write("\r")
                    sys.stdout.write("\u001b[1A")
                    curr -= 1

            elif key == DOWN:
                if curr < size - 1:
                    sys.stdout.write("\r")
                    sys.stdout.write("\u001b[1B")
                    curr += 1


def input_write(prompt: Any = "", edit: Any = "") -> str:
    """
    Based on builtin function 'input'.
    Difference is that argument 'edit' is shown at start (with argument 'prompt') and can be edited.

    Parameters
    ----------
    prompt : `optional`, default: `" "`
                                    - The prompt string, if given, is printed to standard output without a trailing newline before reading input
    edit : `str`, `optional`, default: `" "`
                                    - String to be edited
    """

    sys.stdout.write(prompt + edit)
    written = list(edit)
    curr = len(edit)
    last_key = ""  # support for uppercase letter 'M', 'K, 'H' and 'P'

    # local constants
    RIGHT = b"M"
    LEFT = b"K"
    ENTER = b"\r"
    BACKSPACE = b"\x08"
    SPECIAL = b"\x00"
    # does not write to 'sys.stdout' when 'IGNORE' is recieved right before (special char)
    IGNORE = [RIGHT, LEFT, b"H", b"P"]

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            # use copy of 'last_key' later (next iteration)
            last_key_copy = last_key
            last_key = key  # store key for later use
            if key == ENTER:
                # cleanup
                sys.stdout.write("\n")
                # return as string
                return "".join(written)

            elif key == RIGHT and last_key_copy == SPECIAL:
                if curr < len(written):
                    sys.stdout.write("\u001b[C")
                    curr += 1

            elif key == LEFT and last_key_copy == SPECIAL:
                if curr > 0:
                    curr -= 1
                    sys.stdout.write("\u001b[D")

            elif key == BACKSPACE:
                if written:  # if has content
                    if curr <= 0:  # if focus is to max left
                        continue
                    # remove last char
                    size = len(written)
                    rest = "".join(written[curr:size])
                    n = len(rest) + 1
                    sys.stdout.write("\u001b[D")
                    sys.stdout.write(rest + " ")
                    # move focus right n times to cleanup
                    sys.stdout.write(f"\u001b[{n}D")
                    curr -= 1  # decrement
                    written.pop(curr)  # remove current

            else:
                # adds support for uppercase letter 'M', 'K, 'H' and 'P'
                if key == SPECIAL:
                    continue
                elif key in IGNORE:
                    if last_key_copy == SPECIAL:
                        continue
                # write letter
                letter = key.decode()
                written.insert(curr, letter)  # add to written
                sys.stdout.write(letter)
                curr += 1  # increment
                size = len(written)
                rest = "".join(written[curr:size])
                sys.stdout.write(rest)
                # move focus left n times to cleanup
                n = size - curr
                if n > 0:  # to prevent when n == 0
                    sys.stdout.write(f"\u001b[{n}D")  # f-string


def input_hidden(prompt: Any = "") -> str:
    """
    Based on builtin function 'input'.
    Displays the prompt but does NOT show new letters as new keys are pressed.
    Adds a weak layer of security.

    Parameters
    ----------
    prompt : `optional`, default: `" "`
        - The prompt string, if given, is printed to standard output without a trailing newline before reading input
    """
    sys.stdout.write(prompt)
    written = []
    last_key = ""

    # local contants
    ENTER = b"\r"
    BACKSPACE = b"\x08"
    SPECIAL = b"\x00"
    # does not append to 'written' when 'IGNORE' is recieved right before (special char)
    IGNORE = [b"M", b"K", b"H", b"P"]

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            last_key_copy = last_key  # use copy of 'last_key' later
            last_key = key  # store key for later use (next iteration)
            if key == ENTER:
                # cleanup
                sys.stdout.write("\n")
                return "".join(written)  # return as string

            elif key == BACKSPACE:
                if written:  # remove last letter if not empty
                    written.pop()

            else:  # adds support for uppercase letter 'M', 'K, 'H' and 'P'
                if key == SPECIAL:
                    continue
                elif key in IGNORE:
                    if last_key_copy == SPECIAL:
                        continue
                # store letter
                letter = key.decode()
                written.append(letter)


class OverloadUnmatched(TypeError):
    """ Custom Error for decorator 'overload """

    def __init__(self, fn, types): TypeError.__init__(
        self,
        f"overload function '{fn}': argument types '{types}' not mathing any instance")


class overload():
    """
    Overload decorator used to overload type arguments.
    NOTE: return type is not making a function distinguishable from another!

    @overload
    def f(a: int, b: int) -> int:
        return a + b

    @overload
    def f(a: str, b: str) -> int:
        return int(a + b)

    >>>f(2, 3) -> 5
    >>>f("2", "3") -> 23
    """

    _uniques = {}

    def __init__(self, function):
        self.fn = function
        self.fn_name = function.__name__
        self.fn_signature = str(list(function.__annotations__.values())[:-1])

        if self.fn_name in overload._uniques.keys():
            overload._uniques[
                self.fn_name][self.fn_signature] = self.fn  # add to old
        else:
            overload._uniques[
                self.fn_name] = {self.fn_signature: self.fn}  # make new

    def __repr__(self):
        return self.fn.__repr__()

    def __str__(self):
        return self.fn.__str__()

    def __call__(self, *args, **kwargs):
        types = [str(type(arg)) for arg in args]
        signature = "[" + ", ".join(types) + "]"
        if not signature in overload._uniques[self.fn_name].keys():
            # no match
            raise OverloadUnmatched(self.fn_name, signature[1:-1])
        func = overload._uniques[self.fn_name][signature]
        return func(*args, **kwargs)


# ===============
# Example ussage
# ===============
if __name__ == "__main__":
    # Example 1
    print("\n# Example 1\n")
    print("Hello world!")
    result1 = selection(
        "good",
        "bad",
        "don't want to talk about it...",
        prompt="How is your day?",
        deco="- ",
        capitalize=True
    )
    print("Result:", result1)

    # Example 2
    print("\n# Example 2\n")
    # Tip: have a space at the end of first argument 'promt' (like "Hello ")
    result2 = input_write("Can't edit this:", "Edit this")
    print("Result:", result2)

    # Example 3
    print("\n# Example 3\n")
    # Tip: have a space at the end of first argument 'promt' (like "Hello ")
    result3 = input_hidden("Can't see what you type:")
    print("Result:", result3)

    # Example 4
    print("\n# Example 4\n")

    @overload
    def my_function(a: int, b: int) -> int:
        return a + b

    @overload
    def my_function(a: str, b: str) -> int:
        return int(a + b)

    print("Result 1:", my_function(2, 3))
    print("Result 2:", my_function("2", "3"))
