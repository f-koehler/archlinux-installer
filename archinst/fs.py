import subprocess
import tempfile
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

from archinst.cmd import run
from archinst.mount import MountEntry, mount_list, mount_single


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
            cmd.append(label[:11].upper())
        else:
            cmd.append(label.upper())
    cmd.append(str(device))
    run(cmd)


def create_btrfs_subvolume(path: Union[str, Path]):
    run(["btrfs", "subvolume", "create", str(path)])


def generate_fs_table():
    fstab = subprocess.check_output(["genfstab", "-U", "/mnt"]).decode()
    with open("/mnt/etc/fstab", "a") as fptr:
        fptr.write(fstab)


class BtrfsSubvolumes:
    MountInfo = Union[str, Tuple[Union[str, Path], List[str]]]

    def __init__(self):
        self.subvolumes: List[Tuple[Union[str, Path],
                                    Optional[MountInfo]]] = []

    def add(self, path: Union[str, Path], mount: Optional[MountInfo] = None):
        self.subvolumes.append((path, mount))

    def apply(self, path: Union[str, Path]):
        with tempfile.TemporaryDirectory() as tmpdir:
            with mount_single(path, tmpdir):
                for subvolume in self.subvolumes:
                    create_btrfs_subvolume(Path(tmpdir) / subvolume[0])

    def mount(self, partition: Union[str, Path]):
        mounts: List[MountEntry] = []
        for subvolume in self.subvolumes:
            if subvolume[1] is None:
                continue
            if isinstance(subvolume[1], str):
                mounts.append(
                    (partition, subvolume[1], ["subvol=" + str(subvolume[0])]))
                continue
            mounts.append((partition, subvolume[1][0],
                           ["subvol=" + str(subvolume[0])] + subvolume[1][1]))
