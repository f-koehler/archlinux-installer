#!/usr/bin/env python
import argparse

from archinst import fs, grub, systemctl, time, user
from archinst.initcpio import mkinitcpio
from archinst.mount import mount
from archinst.part import PartitionLayout
from archinst.pkg import pacstrap
from archinst.reflector import run_reflector
from archinst import git
from archinst import cmd

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("drive")
    args = parser.parse_args()

    layout = PartitionLayout.create_empty_gpt(args.drive)
    part_efi = layout.append("200MiB", "fat32")
    part_swap = layout.append("2000MiB", "linux-swap")
    part_root = layout.append("100%", "btrfs")

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
                "networkmanager",
                "ansible",
            ]
        )
        run_reflector("Germany")

        time.set_timezone("Europe/Berlin")
        time.enable_ntp()
        mkinitcpio()
        grub.install_grub_efi()

        systemctl.enable("NetworkManager.service")

        user.add_normal_user("fkoehler")
        user.add_sudoer("fkoehler")
        user.set_password("fkoehler", "test")
        user.set_password("root", "root")

        git.clone(
            "https://github.com/f-koehler/dotfiles.git",
            "/mnt/home/fkoehler/code/dotfiles",
        )
        cmd.run_chroot(
            ["./run"],
            username="fkoehler",
            group="fkoehler",
            cwd="/home/fkoehler/code/dotfiles",
        )
