from pathlib import Path
from typing import Union

from archinst.cmd import run


def clear_disk(disk: Union[str, Path], label: str = "gpt"):
    run(["parted", "-s", str(disk), "mklabel", label])
