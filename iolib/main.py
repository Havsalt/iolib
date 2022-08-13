"""
Main content of iolib
"""

import sys
import msvcrt
import threading
from typing import Any, Callable
from collections.abc import Iterable


__all__ = [
    "selection",
    "input_write",
    "input_hidden",
    "IODisplay",
    "OverloadUnmatched",
    "overload"
]


# activate ANSI escape codes
import os as _os
_os.system("")
del _os

# constants
UP = b"H"
DOWN = b"P"
RIGHT = b"M"
LEFT = b"K"
ENTER = b"\r"
BACKSPACE = b"\x08"
SPECIAL = b"\x00"
IGNORE = [RIGHT, LEFT, b"H", b"P"]

ANSI_UP = "\u001b[A"
ANSI_DOWN = "\u001b[B"
ANSI_RIGHT = "\u001b[C"
ANSI_LEFT = "\u001b[D"


def selection(*options, active: str = " >", passive: str = "> ", wrap: bool = False) -> Any:
    """Navigate up or down to select an option. Use PgUp/PgDown to navigate between options

    Args:
        active (str, optional): active decorative string. Defaults to " >".
        passive (str, optional): decorative string. Defaults to "> ".
        wrap (bool, optional): wraps around when hitting an end. Defaults to False.

    Raises:
        TypeError: if no option is supplied

    Returns:
        Any: selected option
    """
    if not options:
        raise TypeError("no option supplied")

    # control variables
    idx = 0
    n_options = len(options)
    longest_option = len(max(options, key=len))
    longest_mode = len(max(passive, active, key=len))
    longest_length = longest_option + longest_mode

    # display options
    sys.stdout.write(active + str(options[0]))
    for option in options[1:]:
        sys.stdout.write("\n" + passive + str(option))
    sys.stdout.write("\r")
    sys.stdout.flush()
    # place cursor at top
    sys.stdout.write(ANSI_UP * (n_options - 1))

    while True:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == ENTER:
                sys.stdout.write("\n")
                sys.stdout.flush()
                return options[idx]

            elif key == DOWN:
                current = idx
                idx += 1
                idx = min(idx, (n_options - 1))
                # reset line
                reset = "\r" + " " * longest_length + "\r"
                sys.stdout.write(reset)
                sys.stdout.write(passive + options[current])
                sys.stdout.write("\r")
                # move cursor
                if idx == current:  # hit end
                    if wrap and n_options > 1:  # wrap around up
                        idx = 0
                        # move
                        sys.stdout.write(ANSI_UP * (n_options - 1))
                else:  # move one line
                    sys.stdout.write(ANSI_DOWN)
                # display current option
                content = active + options[idx]
                sys.stdout.write(content)
                sys.stdout.write("\r")
                sys.stdout.flush()

            elif key == UP:
                current = idx
                idx -= 1
                idx = max(idx, 0)
                # reset line
                reset = "\r" + " " * longest_length + "\r"
                sys.stdout.write(reset)
                sys.stdout.write(passive + options[current])
                sys.stdout.write("\r")
                # move cursor
                if idx == current:  # hit end
                    if wrap and n_options > 1:  # wrap around up
                        idx = (n_options - 1)
                        # move
                        sys.stdout.write(ANSI_DOWN * (n_options - 1))
                else:  # move one line
                    sys.stdout.write(ANSI_UP)
                # display current option
                content = active + options[idx]
                sys.stdout.write(content)
                sys.stdout.write("\r")
                sys.stdout.flush()


def input_write(prompt: Any = "", edit: Any = "", /) -> str:
    """Take user input with option to start with editable text

    Args:
        prompt (Any, optional): prompt presented to the user. Defaults to "".
        edit (Any, optional): initial text, editable. Defaults to "".

    Returns:
        str: written string
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
                sys.stdout.flush()
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


def input_hidden(prompt: Any = "", /) -> str:
    """Take user input without displaying the keys pressed

    Used as a weak layer of security

    Args:
        prompt (Any, optional): prompt presented to the user. Defaults to "".

    Returns:
        str: written string
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
                sys.stdout.flush()
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


class IODisplay:
    """IODisplay offers a chat like functionality
    TODO: add event system for flush protection
    """

    def __init__(self, prompt: str = "", /, lines: int = 4, *, dispatch_on_enter: bool = True):
        """Innit an IODisplay

        Args:
            prompt (str, optional): prompt presented to the user. Defaults to "".
            lines (int, optional): number of lines buffered. Defaults to 4.
        """
        self.prompt = prompt
        self.lines = lines
        self.callback = None
        self.dispatch_on_enter = dispatch_on_enter
        self._running = False
        self._written = []  # currently typed (as list)
        self._regestry = ["" for _ in range(lines)]  # filled regestry
        self._thread = None

    def start(self, *, threaded: bool = True, callback: Callable = None) -> None:
        """Start the IODisplay instance

        Args:
            threaded (bool, optional): whether to thread the process. Defaults to True.
            callback (Callable, optional): callback called on 'Enter' keypress. Defaults to None.
        """
        self.callback = callback
        if threaded:
            self._thread = threading.Thread(name=self.__class__.__name__,
                                            target=self._start)
            self._thread.start()
        else:
            self._thread = None
            self._start()

    def _start(self) -> None:  # inner start
        """Internal start. May have been started in a new Thread
        TODO: improve support for moving the cursor Left/Right
        """
        self._running = True
        # display lines and prompt
        self._render_lines(init=True)
        # keyboard info
        curr = 0
        last_key = ""  # support for uppercase letter 'M', 'K, 'H' and 'P'

        while self._running:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                # use copy of 'last_key' later (next iteration)
                last_key_copy = last_key
                last_key = key  # store key for later use
                if key == ENTER:
                    # 'get' also flushes when 'dispatch=True'
                    if curr != 0:
                        sys.stdout.write(ANSI_LEFT * curr)
                    string = self.get(dispatch=self.dispatch_on_enter)
                    # call callback with currently written string
                    if self.callback != None:
                        self.callback(string)
                    # reset states
                    curr = 0
                    last_key = ""

                elif key == RIGHT and last_key_copy == SPECIAL:
                    if curr < len(self._written):
                        sys.stdout.write("\u001b[C")
                        curr += 1
                        sys.stdout.flush()

                elif key == LEFT and last_key_copy == SPECIAL:
                    if curr > 0:
                        curr -= 1
                        sys.stdout.write("\u001b[D")
                        sys.stdout.flush()

                elif key == BACKSPACE:
                    if self._written:  # if has content
                        if curr <= 0:  # if focus is to max left
                            continue
                        # remove last char
                        size = len(self._written)
                        rest = "".join(self._written[curr:size])
                        sys.stdout.write("\u001b[D")
                        sys.stdout.write(rest + " ")
                        # move focus right n times to cleanup
                        n = len(rest) + 1
                        sys.stdout.write(f"\u001b[{n}D")
                        curr = max(0, curr - 1)  # decrement
                        self._written.pop(curr)  # remove current
                        sys.stdout.flush()

                else:
                    # adds support for uppercase letter 'M', 'K, 'H' and 'P'
                    if key == SPECIAL:
                        continue
                    elif key in IGNORE:
                        if last_key_copy == SPECIAL:
                            continue
                    # write letter
                    letter = key.decode()
                    self._written.insert(curr, letter)  # add to written
                    sys.stdout.write(letter)
                    curr += 1  # increment
                    size = len(self._written)
                    rest = "".join(self._written[curr:size])
                    sys.stdout.write(rest)
                    # move focus left n times to cleanup
                    n = size - curr
                    if n > 0:  # to prevent when n == 0
                        sys.stdout.write(f"\u001b[{n}D")  # f-string
                    sys.stdout.flush()

    def stop(self, *, dispatch: bool = True) -> None:
        """Stops the IODisplay instance

        TODO: address known issue with unexpected behaviour: \\n
        """
        self._running = False
        if self._thread != None:
            self._thread.join()
            self._thread = None
        if dispatch:
            self._clear_lines()
            sys.stdout.flush()

    def push(self, o: Any, /, *, flush: bool = True) -> None:
        """Push a new object to the fixed size regestry

        Args:
            o (Any): any object (supporting __str__())
            update (bool, optional): whether to flush changes. Defaults to True.
        """
        self._clear_lines()
        if isinstance(o, Iterable) and (not isinstance(o, str)):
            self._regestry.extend(map(str, o))
            self._regestry = self._regestry[len(o):]  # cut out front
        else:
            self._regestry.append(str(o))
            _first_element = self._regestry.pop(0)  # pop front
        if flush:
            self._render_lines()

    def clear(self, *, flush: bool = True) -> None:
        """Clear all elements from the fixed size regestry

        Args:
            flush (bool, optional): whether to flush changes. Defaults to True.
        """
        self._clear_lines(flush=(not flush))
        self._regestry = ["" for _ in range(self.lines)]
        if flush:
            self._render_lines()

    def get(self, *, dispatch: bool = True) -> str:
        """Returns the currently written string

        Args:
            dispatch (bool, optional): whether to start over. Defaults to True.

        Returns:
            str: currently written string
        """
        string = "".join(self._written)
        if dispatch:
            if self._written != []:
                reset = (" " * len(self._written)
                         + ANSI_LEFT * len(self._written))
                sys.stdout.write(reset)
                self._written = []
                sys.stdout.flush()
        return string

    def _clear_lines(self, flush: bool = False) -> None:
        """Clear displayed lines

        Args:
            flush (bool, optional): whether to flush. Defaults to False.
        """
        buffer = ""
        buffer += ANSI_UP * (self.lines) + "\r"
        for element in self._regestry:
            reset = " " * len(element) + "\r"
            buffer += reset
            buffer += ANSI_DOWN
        sys.stdout.write(buffer)
        if flush:
            sys.stdout.flush()

    def _render_lines(self, *, init: bool = False) -> None:
        """Render content

        Args:
            init (bool, optional): whether to treat as initial call. Defaults to False.
        """
        if not init:
            sys.stdout.write(ANSI_UP * (self.lines) + "\r")
        content = "\n".join(self._regestry
                            + [self.prompt + self.get(dispatch=False)])
        sys.stdout.write(content)
        sys.stdout.flush()


class OverloadUnmatched(TypeError):
    """Custom Error for decorator 'overload
    """

    def __init__(self, fn, types): TypeError.__init__(
        self,
        f"overload function '{fn}': argument types '{types}' not mathing any instance")


class overload():
    """Overload decorator used to overload type arguments

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
        self.fn_signature = list(function.__annotations__.values())
        if "return" in function.__annotations__.keys():
            self.fn_signature.pop()  # remove return type from signature

        if self.fn_name in overload._uniques.keys():
            overload._uniques[
                self.fn_name][str(self.fn_signature)] = self.fn  # add to old
        else:
            overload._uniques[
                self.fn_name] = {str(self.fn_signature): self.fn}  # make new

    def __repr__(self):
        return self.fn.__repr__()

    def __str__(self):
        return self.fn.__str__()

    def __call__(self, *args, **kwargs):
        types = [str(type(arg)) for arg in (args + tuple(kwargs.values()))]
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
    print("How is your day?")
    result1 = selection(
        "Good",
        "Bad",
        "I can't remember",
        active=" > ",
        passive="> ",
        wrap=True
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
