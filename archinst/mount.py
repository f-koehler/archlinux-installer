from pathlib import Path
from typing import Union

from archinst.cmd import run


def umount(path: Union[str, Path]):
    run(["umount", str(path)])


def swapon(device: Union[str, Path]):
    run(["swapon", str(device)])


def swapoff(device: Union[str, Path]):
    run(["swapoff", str(device)])
