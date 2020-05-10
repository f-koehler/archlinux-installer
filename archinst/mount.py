from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from typing import List, Optional, Tuple, Union

from archinst.cmd import run

LOGGER = getLogger(__name__)

MountEntry = Union[Tuple[Union[str, Path], Union[str, Path]],
                   Tuple[Union[str, Path], Union[str, Path], List[str]]]


def sync():
    run(["sync"])


def mount(device: Union[str, Path],
          mountpoint: Union[str, Path],
          options: Optional[List[str]] = None):
    LOGGER.info("mount: %s", str(device))
    device = str(device)
    mountpoint = str(mountpoint)

    Path(mountpoint).mkdir(parents=True, exist_ok=True)

    command = ["mount"]
    if options:
        command.append("-o")
        command += options
    command += [device, mountpoint]
    run(command)


def unmount(path: Union[str, Path]):
    LOGGER.info("unmount: %s", str(path))
    sync()
    run(["umount", str(path)])


def swapon(device: Union[str, Path]):
    LOGGER.info("swapon: %s", str(device))
    run(["swapon", str(device)])


def swapoff(device: Union[str, Path]):
    LOGGER.info("swapoff: %s", str(device))
    sync()
    run(["swapoff", str(device)])


@contextmanager
def mount_single(device: Union[str, Path],
                 mountpoint: Union[str, Path],
                 options: Optional[List[str]] = None):
    try:
        if mountpoint == "[SWAP]":
            yield swapon(device)
        else:
            yield mount(device, mountpoint, options)
    finally:
        if mountpoint == "[SWAP]":
            swapoff(device)
        else:
            unmount(mountpoint)


@contextmanager
def mount_list(entries: List[MountEntry]):
    try:
        for entry in entries:
            if entry[1] == "[SWAP]":
                swapon(entry[0])
            else:
                mount(*entry)
        yield
    finally:
        for entry in entries[::-1]:
            try:
                if entry[1] == "[SWAP]":
                    swapoff(entry[0])
                else:
                    unmount(entry[1])
            except:
                pass
