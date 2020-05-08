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


def create_fs_btrfs(device: Union[str, Path], label: Optional[str] = None):
    cmd = ["mkfs.btrfs", "-f"]
    if label:
        cmd += ["-L", label]
    cmd.append(str(device))
    run(cmd)


def create_fs_vfat32(device: Union[str, Path], label: Optional[str] = None):
    cmd = ["mkfs.vfat", "-F", "32"]
    if label:
        cmd.append("-n")
        if len(label) > 11:
            cmd.append(label[:11])
        else:
            cmd.append(label)
    cmd.append(str(device))
    run(cmd)


def create_btrfs_subvolume(path: Union[str, Path]):
    run(["btrfs", "subvolume", "create", str(path)])


def generate_fs_table():
    fstab = subprocess.check_output(["genfstab", "-U", "/mnt"]).decode()
    with open("/mnt/etc/fstab", "a") as fptr:
        fptr.write(fstab)
