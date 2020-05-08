#!/usr/bin/env python
import argparse

from archinst import (cmd, fs, git, grub, initcpio, mount, part, pkg,
                      reflector, time, user)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("drive")
    args = parser.parse_args()
    disk = args.drive

    part.clear_disk(disk, "gpt")
    cmd.run([
        "parted", "-s", "-a", "optimal", disk, "mkpart", "primary", "fat32",
        "0%", "200MiB"
    ])
    cmd.run([
        "parted", "-s", "-a", "optimal", disk, "mkpart", "primary",
        "linux-swap", "200MiB", "2000MiB"
    ])
    cmd.run([
        "parted", "-s", "-a", "optimal", disk, "mkpart", "primary", "btrfs",
        "2000MiB", "100%"
    ])

    fs.create_fs_vfat32(disk + "1", "efi")
    fs.create_fs_swap(disk + "2", "arch_swap")
    fs.create_fs_btrfs(disk + "3", "arch_root")

    with mount.Mount(disk + "3", "/mnt"):
        fs.create_btrfs_subvolume("/mnt/@")
        fs.create_btrfs_subvolume("/mnt/@home")
        fs.create_btrfs_subvolume("/mnt/@snapshots")

    reflector.run_reflector(False, "Germany")

    with mount.Swap(disk + "2"), mount.Mount(
            disk + "3", "/mnt",
        ["subvol=@"]), mount.Mount(disk + "3", "/mnt/home",
                                   ["subvol=@home"]), mount.Mount(
                                       disk + "3", "/mnt/.snapshots",
                                       ["subvol=@snapshots"]), mount.Mount(
                                           disk + "1", "/mnt/boot/efi"):
        pkg.pacstrap([
            "base", "base-devel", "linux", "linux-firmware", "btrfs-progs",
            "grub-btrfs"
        ])
        reflector.run_reflector(True, "Germany")
        fs.generate_fs_table()
        time.set_timezone("Europe/Berlin")
        time.enable_ntp()
        initcpio.mkinitcpio()
        grub.install_grub_efi(disk)

        user.add_normal_user("fkoehler")
        git.clone("https://github.com/f-koehler/playbooks.git",
                  "/home/fkoehler/code/playbooks")
        git.clone("https://github.com/f-koehler/dotfiles.git",
                  "/home/fkoehler/code/dotfiles")
