import subprocess
import tempfile
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

from archinst.cmd import run
from archinst.mount import MountEntry, mount, mount_list, mount_single
from archinst.part import Partition


class FileSystem:
    def __init__(self,
                 partition: Partition,
                 label: Optional[str] = None,
                 mount_point: Optional[Union[str, Path]] = None,
                 mount_options: Optional[List[str]] = None,
                 mount_type: Optional[str] = None):
        self.partition = partition
        self.label = label
        self.mount_point = mount_point
        self.mount_options = mount_options
        self.mount_type = mount_type

    @staticmethod
    def create_ext4(partition: Partition,
                    label: Optional[str] = None,
                    mount_point: Optional[Union[str, Path]] = None,
                    mount_options: Optional[List[str]] = None):
        cmd = ["mkfs.ext4", "-F"]
        if label:
            cmd += ["-L", label]
        cmd.append(partition.device)
        run(cmd)

        return FileSystem(partition,
                          label=label,
                          mount_point=mount_point,
                          mount_type="ext4",
                          mount_options=mount_options)

    @staticmethod
    def create_btrfs(partition: Partition,
                     label: Optional[str] = None,
                     mount_point: Optional[Union[str, Path]] = None,
                     mount_options: Optional[List[str]] = None):
        cmd = ["mkfs.btrfs", "-f"]
        if label:
            cmd += ["-L", label]
        cmd.append(partition.device)
        run(cmd)

        return FileSystem(partition,
                          label=label,
                          mount_point=mount_point,
                          mount_type="btrfs",
                          mount_options=mount_options)

    @staticmethod
    def create_vfat32(partition: Partition,
                      label: Optional[str] = None,
                      mount_point: Optional[Union[str, Path]] = None,
                      mount_options: Optional[List[str]] = None):
        cmd = ["mkfs.vfat", "-F", "32"]
        if label:
            cmd.append("-n")
            cmd.append(label[:11].upper())
        cmd.append(partition.device)
        run(cmd)

        return FileSystem(partition,
                          label=label,
                          mount_point=mount_point,
                          mount_type="btrfs",
                          mount_options=mount_options)

    @staticmethod
    def create_swap(partition: Partition,
                    label: Optional[str] = None,
                    mount_options: Optional[List[str]] = None):
        cmd = ["mkswap", "-f"]
        if label:
            cmd += ["-L", label]
        cmd.append(partition.device)
        run(cmd)

        return FileSystem(partition,
                          label=label,
                          mount_point="[SWAP]",
                          mount_type="swap",
                          mount_options=mount_options)


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
        return mount_list(mounts)
