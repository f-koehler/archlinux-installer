from contextlib import contextmanager
from logging import getLogger
from pathlib import Path
from typing import Union

from archinst.cmd import run

LOGGER = getLogger(__name__)


def mount(device: Union[str, Path], mountpoint: Union[str, Path]):
    LOGGER.info("mount: %s", str(device))
    device = str(device)
    mountpoint = str(mountpoint)
    run(["mount", device, mountpoint])


def umount(path: Union[str, Path]):
    LOGGER.info("unmount: %s", str(device))
    run(["umount", str(path)])


def swapon(device: Union[str, Path]):
    LOGGER.info("swapon: %s", str(device))
    run(["swapon", str(device)])


def swapoff(device: Union[str, Path]):
    LOGGER.info("swapoff: %s", str(device))
    run(["swapoff", str(device)])


@contextmanager
def Mount(device: Union[str, Path], mountpoint: Union[str, Path]):
    try:
        mount(device, mountpoint)
    finally:
        unmount(mountpoint)


@contextmanager
def Swap(device: Union[str, Path]):
    try:
        swapon(device)
    finally:
        swapoff(device)
