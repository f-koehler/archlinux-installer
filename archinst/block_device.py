from pathlib import Path
from subprocess import check_output
from typing import Union


class BlockDevice:
    def __init__(self, path: Union[str, Path]):
        self.path = str(path)

    def get_uuid(self) -> str:
        return check_output(["lsblk", "-no", "UUID", self.path]).decode().strip()
