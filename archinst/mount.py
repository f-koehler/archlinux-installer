import subprocess
from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from typing import List, Union

from archinst.cmd import run
from archinst.fs import FileSystem

LOGGER = getLogger(__name__)


def mount_filesystem(filesystem: FileSystem):
    if filesystem.mount_point is None:
        return

    cmd: List[str] = []

    if filesystem.type_ == "swap":
        cmd = ["swapon"]
        if filesystem.mount_options:
            cmd += ["-o", ",".join(filesystem.mount_options)]
        cmd.append(filesystem.block_device.path)
    else:
        Path(filesystem.mount_point).mkdir(parents=True, exist_ok=True)
        cmd = ["mount", "-t", filesystem.type_]
        if filesystem.mount_options:
            cmd += ["-o", ",".join(filesystem.mount_options)]
        cmd += [filesystem.block_device.path, filesystem.mount_point]

    run(cmd)
    filesystem.mounted = True


def is_mounted(filesystem: FileSystem) -> bool:
    if filesystem.mount_point is None:
        return False

    if filesystem.type_ == "swap":
        with open("/proc/swaps", "r") as fptr:
            for line in fptr.readlines()[1:]:
                device = line.split()[0].strip()
                if Path(device) == Path(filesystem.block_device.path):
                    return True
        return False

    with open("/proc/mounts", "r") as fptr:
        for line in fptr.readlines():
            device = line.split()[0].strip()
            if Path(device) == Path(filesystem.block_device.path):
                return True

    return False


def unmount_filesystem(filesystem: FileSystem):
    cmd: List[str] = []

    if filesystem.type_ == "swap":
        cmd = ["swapoff", filesystem.block_device.path]
    else:
        cmd = ["umount", filesystem.mount_point]

    run(cmd)
    filesystem.mounted = False


@contextmanager
def mount(filesystem: Union[FileSystem, List[FileSystem]]):
    if isinstance(filesystem, FileSystem):
        filesystems = [
            filesystem,
        ]
    else:
        filesystems = filesystem

    try:
        for fs in filesystems:
            mount_filesystem(fs)
        yield
    finally:
        for fs in reversed(filesystems):
            try:
                unmount_filesystem(fs)
            except:
                pass
