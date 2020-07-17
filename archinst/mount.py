import subprocess
from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from typing import List, Union, Dict
import traceback

from archinst.cmd import run
from archinst.fs import FileSystem

LOGGER = getLogger(__name__)


class UnmountingExceptions(Exception):
    def __init__(self, exceptions: Dict[FileSystem, Exception]):
        self.exceptions = exceptions
        super().__init__(
            "{\n"
            + "\n\t".join(
                (fs.mount_point + ": " + str(exceptions[fs]) for fs in exceptions)
            )
            + "\n}"
        )


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

    unmount_exceptions: Dict[FileSystem, Exception] = {}

    try:
        for fs in filesystems:
            mount_filesystem(fs)
        yield
    finally:
        for fs in reversed(filesystems):
            try:
                unmount_filesystem(fs)
            except Exception as ex:
                LOGGER.error(
                    'unmounting the filesystem mounted at "%s" raised an exception',
                    fs.mount_point,
                )
                LOGGER.error("I will unmount the remaining filesystems")
                unmount_exceptions[fs] = ex

    if unmount_exceptions:
        raise UnmountingExceptions(unmount_exceptions)
