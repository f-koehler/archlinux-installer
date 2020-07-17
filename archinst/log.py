# from logging import getLogger
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)


def get_logger(name: Optional[str] = None):
    return logging.getLogger(name)
