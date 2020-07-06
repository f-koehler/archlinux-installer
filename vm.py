#!/usr/bin/env python
import argparse

from archinst import fs
from archinst.mount import mount
from archinst.part import PartitionLayout
from archinst.reflector import run_reflector
from archinst.pkg import pacstrap

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("drive")
    args = parser.parse_args()

    layout = PartitionLayout.create_empty_gpt(args.drive)
    part_efi = layout.append("fat32", "200MiB")
    part_swap = layout.append("linux-swap", "2000MiB")
    part_root = layout.append("btrfs", "100%")

    fs_root = fs.create_btrfs(part_root, "arch_root", "/mnt/")
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
        run_reflector("Germany", "/mnt")

    # with subvolumes.mount(disk + "3"), layout.mount(disk):
    #     time.set_timezone("Europe/Berlin")
    #     time.enable_ntp()
    #     initcpio.mkinitcpio()
    #     grub.install_grub_efi(disk)

    #     user.add_normal_user("fkoehler")
