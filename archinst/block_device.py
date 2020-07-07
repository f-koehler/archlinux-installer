from pathlib import Path
from typing import Union


class BlockDevice:
    def __init__(self, path: Union[str, Path]):
        self.path = str(path)
