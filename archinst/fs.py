import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Union

from archinst.cmd import run
from archinst.part import Partition


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


class BtrfsFileSystem(FileSystem):
    def __init__(
        self,
        partition: Partition,
        label: Optional[str] = None,
        mount_point: Optional[Union[str, Path]] = None,
        mount_options: Optional[List[str]] = None,
    ):
        super().__init__(partition, "btrfs", label, mount_point, mount_options)


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


# class BtrfsSubvolume:
#     def __init__(
#         self,
#         name: Union[str, Path],
#         path: Optional[Union[str, Path]] = None,
#         mount_options: Optional[List[str]] = None,
#     ):
#         self.name = str(name)
#         self.path = Path(name) if path is None else Path(path)
#         self.mount_options = mount_options

#         cmd = ["btrfs", "subvolume", "create", self.name]
#         run(cmd)


# def create_btrfs_subvolume(path: Union[str, Path]):
#     run(["btrfs", "subvolume", "create", str(path)])


# def generate_fs_table():
#     fstab = subprocess.check_output(["genfstab", "-U", "/mnt"]).decode()
#     with open("/mnt/etc/fstab", "a") as fptr:
#         fptr.write(fstab)


# class BtrfsSubvolumes:
#     MountInfo = Union[str, Tuple[Union[str, Path], List[str]]]

#     def __init__(self):
#         self.subvolumes: List[Tuple[Union[str, Path], Optional[MountInfo]]] = []

#     def add(self, path: Union[str, Path], mount: Optional[MountInfo] = None):
#         self.subvolumes.append((path, mount))

#     def apply(self, path: Union[str, Path]):
#         with tempfile.TemporaryDirectory() as tmpdir:
#             with mount_single(path, tmpdir):
#                 for subvolume in self.subvolumes:
#                     create_btrfs_subvolume(Path(tmpdir) / subvolume[0])

#     def mount(self, partition: Union[str, Path]):
#         mounts: List[MountEntry] = []
#         for subvolume in self.subvolumes:
#             if subvolume[1] is None:
#                 continue
#             if isinstance(subvolume[1], str):
#                 mounts.append(
#                     (partition, subvolume[1], ["subvol=" + str(subvolume[0])])
#                 )
#                 continue
#             mounts.append(
#                 (
#                     partition,
#                     subvolume[1][0],
#                     ["subvol=" + str(subvolume[0])] + subvolume[1][1],
#                 )
#             )
#         return mount_list(mounts)
