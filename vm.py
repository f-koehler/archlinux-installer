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
    fs.create_fs_ext4(disk + "2", "arch_root")

    reflector.run_reflector(False, "Germany")

    with mount.Swap(disk + "1"), mount.Mount(disk + "2", "/mnt"):
        pkg.pacstrap(["base", "base-devel", "linux", "linux-firmware"])
        reflector.run_reflector(True, "Germany")
        fs.generate_fs_table()
        time.set_timezone("Europe/Berlin")
        time.enable_ntp()
        initcpio.mkinitcpio()
        grub.install_grub_bios(disk)
