#!/usr/bin/env python
import argparse

from archinst import (cmd, crypt, fs, git, grub, initcpio, mount, part, pkg,
                      reflector, time, user)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("drive")
    args = parser.parse_args()
    disk = args.drive

    layout = part.PartitionLayout()
    layout.append("fat32", "200MiB", "/mnt/boot/efi")
    layout.append("linux-swap", "2000MiB", "[SWAP]")
    layout.append("btrfs", "100%")
    layout.apply(disk)

    fs.create_fs_vfat32(disk + "1", "efi")
    fs.create_fs_swap(disk + "2", "arch_swap")

    crypt.create_luks_container(disk + "3", "test")
    with crypt.luks_container(disk + "3", "crypt_root", "test"):
        fs.create_fs_btrfs("/dev/mapper/crypt_root", "arch_root")

        subvolumes = fs.BtrfsSubvolumes()
        subvolumes.add("@", "/mnt/")
        subvolumes.add("@home", "/mnt/home")
        subvolumes.add("@snapshots", "/mnt/.snapshots")
        subvolumes.add("@/var/log", "/mnt/var/log")
        subvolumes.add("/var/cache/pacman/pkg")
        subvolumes.apply("/dev/mapper/crypt_root")

        reflector.run_reflector(False, "Germany")

        with subvolumes.mount("/dev/mapper/crypt_root"), layout.mount(disk):
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
