import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Union
from logging import getLogger

from archinst.cmd import run
from archinst.part import Partition

LOGGER = getLogger(__name__)


class FileSystem:
    def __init__(
        self,
        partition: Partition,
        type_: str,
        label: Optional[str] = None,
        mount_point: Optional[Union[str, Path]] = None,
        mount_options: Optional[List[str]] = None,
    ):
        self.partition = partition
        self.type_ = type_
        self.label = label
        self.mount_point = str(mount_point)
        self.mount_options = mount_options
        self.mounted = False


class BtrfsFileSystem(FileSystem):
    def __init__(
        self,
        partition: Partition,
        label: Optional[str] = None,
        mount_point: Optional[Union[str, Path]] = None,
        mount_options: Optional[List[str]] = None,
    ):
        super().__init__(partition, "btrfs", label, mount_point, mount_options)

    def create_subvolume(self, name: str) -> FileSystem:
        if self.mount_point is None:
            raise RuntimeError("btrfs filesystem does not have mountpoint")

        if not self.mounted:
            raise RuntimeError("base filesystem is not mounted")

        subvolume_path = Path(self.mount_point) / name
        subvolume_path.parent.mkdir(parents=True, exist_ok=True)

        cmd = ["btrfs", "subvolume", "create", name]
        run(cmd, cwd=self.mount_point)

        mount_options = [] if self.mount_options is None else self.mount_options
        mount_options.append("subvol=" + name)

        return FileSystem(
            self.partition,
            self.type_,
            mount_point=Path(self.mount_point) / name,
            mount_options=mount_options,
        )


def create_ext4(
    partition: Partition,
    label: Optional[str] = None,
    mount_point: Optional[Union[str, Path]] = None,
    mount_options: Optional[List[str]] = None,
) -> FileSystem:
    cmd = ["mkfs.ext4", "-F"]
    if label:
        cmd += ["-L", label]
    cmd.append(partition.device)
    run(cmd)

    return FileSystem(
        partition,
        "ext4",
        label=label,
        mount_point=mount_point,
        mount_options=mount_options,
    )


def create_btrfs(
    partition: Partition,
    label: Optional[str] = None,
    mount_point: Optional[Union[str, Path]] = None,
    mount_options: Optional[List[str]] = None,
) -> BtrfsFileSystem:
    cmd = ["mkfs.btrfs", "-f"]
    if label:
        cmd += ["-L", label]
    cmd.append(partition.device)
    run(cmd)

    return BtrfsFileSystem(
        partition, label=label, mount_point=mount_point, mount_options=mount_options,
    )


def create_vfat32(
    partition: Partition,
    label: Optional[str] = None,
    mount_point: Optional[Union[str, Path]] = None,
    mount_options: Optional[List[str]] = None,
) -> FileSystem:
    cmd = ["mkfs.vfat", "-F", "32"]
    if label:
        cmd.append("-n")
        cmd.append(label[:11].upper())
    cmd.append(partition.device)
    run(cmd)

    return FileSystem(
        partition,
        "vfat",
        label=label,
        mount_point=mount_point,
        mount_options=mount_options,
    )


def create_swap(
    partition: Partition,
    label: Optional[str] = None,
    mount_options: Optional[List[str]] = None,
) -> FileSystem:
    cmd = ["mkswap", "-f"]
    if label:
        cmd += ["-L", label]
    cmd.append(partition.device)
    run(cmd)

    return FileSystem(
        partition,
        "swap",
        label=label,
        mount_point="[SWAP]",
        mount_options=mount_options,
    )


def generate_fstab(mount_point: Union[str, Path] = "/mnt"):
    fstab = subprocess.check_output(["genfstab", "-U", str(mount_point)]).decode()
    fstab_file = Path(mount_point) / "etc" / "fstab"
    fstab_file.parent.mkdir(parents=True, exist_ok=True)
    with open(fstab_file, "a") as fptr:
        fptr.write(fstab)
