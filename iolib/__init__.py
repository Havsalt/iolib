"""
IO library inspired by the builtin function 'input'
* selection
* input_write
* input_hidden
* IODisplay

Also contains decorator 'overload'
- Used to define a function multiple times
- Distinguishes by looking at argument types
- Return types does not make it distinguisable

Latest supported version of Python: 3.8.2
"""

__version__ = "0.3.5"
__author__ = "FloatingInt"

__all__ = [
    "selection",
    "input_write",
    "input_hidden",
    "OverloadUnmatched",
    "overload"
]

from .main import *
