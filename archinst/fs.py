import subprocess
from pathlib import Path
from typing import List, Optional, Union

from archinst.block_device import BlockDevice
from archinst.cmd import run
from archinst import log

LOGGER = log.get_logger(__name__)


class FileSystem:
    def __init__(
        self,
        block_device: BlockDevice,
        type_: str,
        label: Optional[str] = None,
        mount_point: Optional[Union[str, Path]] = None,
        mount_options: Optional[List[str]] = None,
    ):
        self.block_device = block_device
        self.type_ = type_
        self.label = label
        self.mount_point = str(mount_point)
        self.mount_options = mount_options
        self.mounted = False


class BtrfsFileSystem(FileSystem):
    def __init__(
        self,
        block_device: BlockDevice,
        label: Optional[str] = None,
        mount_point: Optional[Union[str, Path]] = None,
        mount_options: Optional[List[str]] = None,
    ):
        super().__init__(block_device, "btrfs", label, mount_point, mount_options)

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
            self.block_device,
            self.type_,
            mount_point=Path(self.mount_point) / name,
            mount_options=mount_options,
        )


def create_ext4(
    block_device: BlockDevice,
    label: Optional[str] = None,
    mount_point: Optional[Union[str, Path]] = None,
    mount_options: Optional[List[str]] = None,
) -> FileSystem:
    cmd = ["mkfs.ext4", "-F"]
    if label:
        cmd += ["-L", label]
    cmd.append(block_device.path)
    run(cmd)

    return FileSystem(
        block_device,
        "ext4",
        label=label,
        mount_point=mount_point,
        mount_options=mount_options,
    )


def create_btrfs(
    block_device: BlockDevice,
    label: Optional[str] = None,
    mount_point: Optional[Union[str, Path]] = None,
    mount_options: Optional[List[str]] = None,
) -> BtrfsFileSystem:
    cmd = ["mkfs.btrfs", "-f"]
    if label:
        cmd += ["-L", label]
    cmd.append(block_device.path)
    run(cmd)

    return BtrfsFileSystem(
        block_device, label=label, mount_point=mount_point, mount_options=mount_options,
    )


def create_vfat32(
    block_device: BlockDevice,
    label: Optional[str] = None,
    mount_point: Optional[Union[str, Path]] = None,
    mount_options: Optional[List[str]] = None,
) -> FileSystem:
    cmd = ["mkfs.vfat", "-F", "32"]
    if label:
        cmd.append("-n")
        cmd.append(label[:11].upper())
    cmd.append(block_device.path)
    run(cmd)

    return FileSystem(
        block_device,
        "vfat",
        label=label,
        mount_point=mount_point,
        mount_options=mount_options,
    )


def create_swap(
    block_device: BlockDevice,
    label: Optional[str] = None,
    mount_options: Optional[List[str]] = None,
) -> FileSystem:
    cmd = ["mkswap", "-f"]
    if label:
        cmd += ["-L", label]
    cmd.append(block_device.path)
    run(cmd)

    return FileSystem(
        block_device,
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
