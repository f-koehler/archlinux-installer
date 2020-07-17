from pathlib import Path
from typing import Union
from tempfile import TemporaryDirectory

from archinst.cmd import run_chroot


def install_yay(username: str, group: str, prefix: Union[str, Path] = "/mnt"):
