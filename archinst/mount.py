from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from typing import List, Optional, Union

from archinst.cmd import run

LOGGER = getLogger(__name__)


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
    run(["umount", str(path)])


def swapon(device: Union[str, Path]):
    LOGGER.info("swapon: %s", str(device))
    run(["swapon", str(device)])


def swapoff(device: Union[str, Path]):
    LOGGER.info("swapoff: %s", str(device))
    run(["swapoff", str(device)])


@contextmanager
def Mount(device: Union[str, Path],
          mountpoint: Union[str, Path],
          options: Optional[List[str]] = None):
    try:
        yield mount(device, mountpoint, options)
    finally:
        unmount(mountpoint)


@contextmanager
def Swap(device: Union[str, Path]):
    try:
        yield swapon(device)
    finally:
        swapoff(device)
