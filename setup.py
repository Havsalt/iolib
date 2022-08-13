from setuptools import setup, find_packages
from iolib import __version__, __author__


# 0.3.4: fixed 'selection'
# 0.3.4: fix 'selection' using a single string as iterable
# 0.3.4: in 'selection', reset cursor position when returning
# 0.3.5: unstable build with overhaul and IODisplay
# 0.4.0: update all remaining functions
# 0.4.0: added IODisplay
__description__ = "IO library inspired by the builtin function 'input'"

setup(
    name="iolib",
    packages=["iolib"],
    version=__version__,
    license="MIT",
    description=__description__,
    author=__author__,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows"
    ]
)
