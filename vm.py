#!/usr/bin/env python
import argparse

from archinst import cmd, fs, git, grub, initcpio, systemctl, time, user
from archinst.mount import mount
from archinst.part import PartitionLayout
from archinst.pkg import pacstrap
from archinst.reflector import run_reflector

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
                "ansible",
                "base",
                "base-devel",
                "btrfs-progs",
                "git",
                "grub-btrfs",
                "linux",
                "linux-firmware",
                "networkmanager",
                "snap-pac",
                "snapper",
            ]
        )
        run_reflector("Germany")

        time.set_timezone("Europe/Berlin")
        time.enable_ntp()
        hooks = initcpio.read_hooks()
        initcpio.insert_hook_after(hooks, "btrfs", "filesystem")
        initcpio.write_hooks(hooks)
        initcpio.mkinitcpio()
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
