#!/usr/bin/env python
import argparse
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Union

from archinst import cmd, fs, grub, mount, part, pkg, reflector, time


def mkinitcpio(root: Union[str, Path] = "/mnt"):
    cmd.run_chroot(["mkinitcpio", "-v", "-P"], root)


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

    reflector.run_reflector(False, "Germany")

    with mount.Swap(disk + "1"), mount.Mount(disk + "2", "/mnt"):
        pkg.pacstrap(["base", "base-devel", "linux", "linux-firmware"])
        reflector.run_reflector(True, "Germany")
        fs.generate_fs_table()
        time.set_timezone("Europe/Berlin")
        time.enable_ntp()
        mkinitcpio()
        grub.install_grub_bios(disk)
