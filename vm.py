#!/usr/bin/env python
import argparse
import re
import subprocess
from pathlib import Path
from typing import Union, List, Optional


def run(command: List[str]):
    subprocess.run(command, check=True)


def run_chroot(command: List[str], root: Union[str, Path] = "/mnt"):
    run(["arch-chroot", str(root)] + command)


def clear_disk(disk: Union[str, Path], label: str = "gpt"):
    run(["parted", "-s", str(disk), "mklabel", label])


def mkinitcpio(root: Union[str, Path] = "/mnt"):
    run_chroot(["mkinitcpio", "-v", "-P"], root)


def umount(path: Union[str, Path]):
    run(["umount", str(path)])


def swapon(device: Union[str, Path]):
    run(["swapon", str(device)])


def swapoff(device: Union[str, Path]):
    run(["swapoff", str(device)])


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


def pacstrap(packages: Union[str, List[str]], root: Union[str, Path] = "/mnt"):
    if isinstance(packages, str):
        run(["pacstrap", str(root), packages])
    else:
        run(["pacstrap", str(root)] + packages)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("drive")
    args = parser.parse_args()
    disk = args.drive

    clear_disk(disk, "msdos")
    subprocess.run([
        "parted", "-s", "-a", "optimal", disk, "mkpart", "primary",
        "linux-swap", "0%", "200MiB"
    ],
                   check=True)

    subprocess.run([
        "parted", "-s", "-a", "optimal", disk, "mkpart", "primary", "ext4",
        "200MiB", "100%"
    ],
                   check=True)

    create_fs_swap(disk + "1", "arch_swap")
    create_fs_ext4(disk + "2", "arch_ext4")

    swapon(disk + "1")
    subprocess.run(["mount", disk + "2", "/mnt"], check=True)

    try:
        subprocess.run([
            "reflector", "--age", "12", "--country", "Germany", "--protocol",
            "https", "--sort", "rate", "--save", "/etc/pacman.d/mirrorlist"
        ],
                       check=True)

        pacstrap(["base", "base-devel", "linux", "linux-firmware"])

        # use retries for reflector
        subprocess.run([
            "reflector", "--age", "12", "--country", "Germany", "--protocol",
            "https", "--sort", "rate", "--save", "/mnt/etc/pacman.d/mirrorlist"
        ],
                       check=True)

        with open("/mnt/etc/fstab", "a") as fptr:
            fptr.write(
                subprocess.check_output(["genfstab", "-U", "/mnt"]).decode())

        subprocess.run([
            "arch-chroot", "/mnt", "ln", "-sf",
            "/usr/share/zoneinfo/Europe/Berlin", "/etc/localtime"
        ],
                       check=True)
        subprocess.run(["arch-chroot", "/mnt", "hwclock", "--systohc"],
                       check=True)

        pacstrap(["grub", "os-prober", "ntfs-3g"])
        subprocess.run(
            ["arch-chroot", "/mnt", "grub-install", "--target=i386-pc", disk],
            check=True)
        subprocess.run([
            "arch-chroot", "/mnt", "grub-mkconfig", "-o", "/boot/grub/grub.cfg"
        ],
                       check=True)

        mkinitcpio()
    finally:
        umount(disk + "2")
        swapoff(disk + "1")
