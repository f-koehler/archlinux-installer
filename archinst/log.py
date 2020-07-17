# from logging import getLogger
import logging
from typing import Optional
from pathlib import Path
import sys


logging.basicConfig(
    level=logging.INFO,
    filename=str(Path(sys.modules["__main__"].__file__).name) + ".log",
    filemode="w",
)


def get_logger(name: Optional[str] = None):
    return logging.getLogger(name)
