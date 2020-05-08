import subprocess
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


def generate_fs_table():
    fstab = subprocess.check_output(["genfstab", "-U", "/mnt"]).decode()
    with open("/mnt/etc/fstab", "a") as fptr:
        fptr.write(fstab)
