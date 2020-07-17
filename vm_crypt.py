#!/usr/bin/env python
import argparse

from archinst import fs, grub, time
from archinst.initcpio import mkinitcpio
from archinst.mount import mount
from archinst.part import PartitionLayout
from archinst.pkg import pacstrap
from archinst.crypt import luks_container
from archinst.reflector import run_reflector

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("drive")
    args = parser.parse_args()

    layout = PartitionLayout.create_empty_gpt(args.drive)
    part_efi = layout.append("200MiB", "fat32")
    part_swap = layout.append("2000MiB", "linux-swap")
    part_root = layout.append("100%")

    with luks_container(part_root, "root", "test") as root_crypt:
        fs_root = fs.create_btrfs(root_crypt, "arch_root", "/mnt/")
        fs_efi = fs.create_vfat32(part_efi, "efi", "/mnt/boot/efi")
        fs_swap = fs.create_swap(part_swap, "arch_swap")

        with mount([fs_root, fs_efi, fs_swap]):
            subvolumes = [
                fs_root.create_subvolume("@"),
                fs_root.create_subvolume("@home"),
                fs_root.create_subvolume("@snapshots"),
                fs_root.create_subvolume("@/var/log"),
            ]
            with mount(subvolumes):
                fs.generate_fstab()

                run_reflector("Germany", "/")
                pacstrap(
                    [
                        "base",
                        "base-devel",
                        "linux",
                        "linux-firmware",
                        "btrfs-progs",
                        "grub-btrfs",
                    ]
                )
                run_reflector("Germany")

                time.set_timezone("Europe/Berlin")
                time.enable_ntp()
                mkinitcpio()
                grub.install_grub_efi()
