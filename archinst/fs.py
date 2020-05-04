from pathlib import Path
from typing import Optional, Union

from archinst.cmd import run


def create_fs_ext4(device: Union[str, Path], label: Optional[str] = None):
    cmd = ["mkfs.ext4", "-F"]
    if label:
        cmd += ["-L", label]
    cmd.append(str(device))
    run(cmd)


def create_fs_swap(device: Union[str, Path], label: Optional[str] = None):
    cmd = ["mkswap", "-f"]
    if label:
        cmd += ["-L", label]
    cmd.append(str(device))
    run(cmd)
