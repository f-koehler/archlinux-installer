#!/usr/bin/env python
import argparse

from archinst import fs
from archinst.mount import mount
from archinst.part import PartitionLayout
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("drive")
    args = parser.parse_args()

    layout = PartitionLayout.create_empty_gpt(args.drive)
    part_efi = layout.append("fat32", "200MiB")
    part_swap = layout.append("linux-swap", "2000MiB")
    part_root = layout.append("btrfs", "100%")

    filesystems = [
        fs.create_btrfs(part_root, "arch_root", "/mnt/"),
        fs.create_vfat32(part_efi, "efi", "/mnt/boot/efi"),
        fs.create_swap(part_swap, "arch_swap"),
    ]

    with mount(filesystems):
        pass
        # subvolumes = [
        #     BtrfsSubvolume("@", "/mnt"),
        #     BtrfsSubvolume("@home", "/mnt/home"),
        #     BtrfsSubvolume("@snapshots", "/mnt/.snapshots"),
        #     BtrfsSubvolume("@/var/log", "/mnt/var/log"),
        # ]

    # subvolumes = fs.BtrfsSubvolumes()
    # subvolumes.add("@", "/mnt/")
    # subvolumes.add("@home", "/mnt/home")
    # subvolumes.add("@snapshots", "/mnt/.snapshots")
    # subvolumes.apply(disk + "3")

    # reflector.run_reflector(False, "Germany")

    # with subvolumes.mount(disk + "3"), layout.mount(disk):
    #     pkg.pacstrap([
    #         "base", "base-devel", "linux", "linux-firmware", "btrfs-progs",
    #         "grub-btrfs"
    #     ])
    #     reflector.run_reflector(True, "Germany")
    #     fs.generate_fs_table()
    #     time.set_timezone("Europe/Berlin")
    #     time.enable_ntp()
    #     initcpio.mkinitcpio()
    #     grub.install_grub_efi(disk)

    #     user.add_normal_user("fkoehler")
