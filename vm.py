#!/usr/bin/env python
import argparse
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Union

from archinst import cmd, fs, mount, part


def mkinitcpio(root: Union[str, Path] = "/mnt"):
    cmd.run_chroot(["mkinitcpio", "-v", "-P"], root)


def pacstrap(packages: Union[str, List[str]], root: Union[str, Path] = "/mnt"):
    if isinstance(packages, str):
        cmd.run(["pacstrap", str(root), packages])
    else:
        cmd.run(["pacstrap", str(root)] + packages)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("drive")
    args = parser.parse_args()
    disk = args.drive

    part.clear_disk(disk, "msdos")
    cmd.run([
        "parted", "-s", "-a", "optimal", disk, "mkpart", "primary",
        "linux-swap", "0%", "200MiB"
    ])

    cmd.run([
        "parted", "-s", "-a", "optimal", disk, "mkpart", "primary", "ext4",
        "200MiB", "100%"
    ])

    fs.create_fs_swap(disk + "1", "arch_swap")
    fs.create_fs_ext4(disk + "2", "arch_ext4")

    with mount.Swap(disk + "1"), mount.Mount(disk + "2", "/mnt"):
        cmd.run([
            "reflector", "--age", "12", "--country", "Germany", "--protocol",
            "https", "--sort", "rate", "--save", "/etc/pacman.d/mirrorlist"
        ])

        pacstrap(["base", "base-devel", "linux", "linux-firmware"])

        # use retries for reflector
        cmd.run([
            "reflector", "--age", "12", "--country", "Germany", "--protocol",
            "https", "--sort", "rate", "--save", "/mnt/etc/pacman.d/mirrorlist"
        ])

        with open("/mnt/etc/fstab", "a") as fptr:
            fptr.write(
                subprocess.check_output(["genfstab", "-U", "/mnt"]).decode())

        cmd.run_chroot([
            "ln", "-sf", "/usr/share/zoneinfo/Europe/Berlin", "/etc/localtime"
        ])
        cmd.run_chroot(["hwclock", "--systohc"])

        pacstrap(["grub", "os-prober", "ntfs-3g"])
        cmd.run_chroot(["grub-install", "--target=i386-pc", disk])
        cmd.run_chroot(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"])

        mkinitcpio()
