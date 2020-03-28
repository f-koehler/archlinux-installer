#!/usr/bin/env python
import argparse
import re
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("drive")
    args = parser.parse_args()
    disk = args.drive

    subprocess.run(["parted", "-s", disk, "mklabel", "msdos"], check=True)
    subprocess.run([
        "parted", "-s", "-a", "optimal", disk, "mkpart", "primary",
        "linux-swap", "0%", "200MiB"
    ],
                   check=True)

    subprocess.run([
        "parted", "-s", "-a", "optimal", disk, "mkpart", "primary", "ext4",
        "200MiB", "100%"
    ],
                   check=True)

    subprocess.run(["mkswap", "-f", "-L", "arch_swap", disk + "1"], check=True)
    subprocess.run(["mkfs.ext4", "-F", "-L", "arch_root", disk + "2"],
                   check=True)

    subprocess.run(["swapon", disk + "1"], check=True)
    subprocess.run(["mount", disk + "2", "/mnt"], check=True)

    try:
        subprocess.run([
            "reflector", "--age", "12", "--country", "Germany", "--protocol",
            "https", "--sort", "rate", "--save", "/etc/pacman.d/mirrorlist"
        ],
                       check=True)
        subprocess.run([
            "pacstrap", "/mnt", "base", "base-devel", "linux", "linux-firmware"
        ],
                       check=True)

        # use retries for reflector
        subprocess.run([
            "reflector", "--age", "12", "--country", "Germany", "--protocol",
            "https", "--sort", "rate", "--save", "/mnt/etc/pacman.d/mirrorlist"
        ],
                       check=True)

        with open("/mnt/etc/fstab", "a") as fptr:
            fptr.write(
                subprocess.check_output(["genfstab", "-U", "/mnt"]).decode())

        subprocess.run([
            "arch-chroot", "/mnt", "ln", "-sf",
            "/usr/share/zoneinfo/Europe/Berlin", "/etc/localtime"
        ],
                       check=True)
        subprocess.run(["arch-chroot", "/mnt", "hwclock", "--systohc"],
                       check=True)

        subprocess.run(["pacstrap", "/mnt", "grub", "os-prober", "ntfs-3g"],
                       check=True)
        subprocess.run(
            ["arch-chroot", "/mnt", "grub-install", "--target=i386-pc", disk],
            check=True)
        subprocess.run([
            "arch-chroot", "/mnt", "grub-mkconfig", "-o", "/boot/grub/grub.cfg"
        ],
                       check=True)

        subprocess.run(["arch-chroot", "/mnt", "mkinitcpio", "-P", "-v"])
    finally:
        subprocess.run(["umount", disk + "2"])
        subprocess.run(["swapoff", disk + "1"])
