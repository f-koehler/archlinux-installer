#!/usr/bin/env python
import argparse

from archinst import cmd, fs, grub, initcpio, mount, part, pkg, reflector, time

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
    fs.create_fs_btrfs(disk + "2", "arch_root")

    with mount.Mount(disk + "2", "/mnt"):
        fs.create_btrfs_subvolume("/mnt/@")
        fs.create_btrfs_subvolume("/mnt/@home")
        fs.create_btrfs_subvolume("/mnt/@snapshots")

    reflector.run_reflector(False, "Germany")

    with mount.Swap(disk + "1"), mount.Mount(
            disk + "2", "/mnt", ["subvol=@"]), mount.Mount(
                disk + "2", "/mnt/home",
                ["subvol=@home"]), mount.Mount(disk + "2", "/mnt/.snapshots",
                                               ["subvol=@snapshots"]):
        pkg.pacstrap([
            "base", "base-devel", "linux", "linux-firmware", "btrfs-progs",
            "grub-btrfs"
        ])
        reflector.run_reflector(True, "Germany")
        fs.generate_fs_table()
        time.set_timezone("Europe/Berlin")
        time.enable_ntp()
        initcpio.mkinitcpio()
        grub.install_grub_bios(disk)
