#!/usr/bin/env python
import subprocess
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("drive")
    args = parser.parse_args()
    disk = args.drive

    subprocess.run(["parted" "-s", disk, "mklabel", "gpt"])
    subprocess.run([
        "parted"
        "-s", "-a", "optimal", disk, "mkpart", "primary", "arch_swap",
        "linux-swap", "0%", "200MiB"
    ])
    subprocess.run(["parted", "-s", disk, "set", "1", "swap", "on"])

    subprocess.run([
        "parted"
        "-s", "-a", "optimal", disk, "mkpart", "primary", "arch_root", "ext4",
        "200MiB", "100%"
    ])
    subprocess.run(["parted", "-s", disk, "set", "1", "root", "on"])
    subprocess.run(["parted", "-s", disk, "set", "1", "boot", "on"])

    subprocess.run(["mkswap", "-f", "-L", "arch_swap", disk + "1"])
    subprocess.run(["mkfs.ext4", "-F", "-L", "arch_root", disk + "2"])

    subprocess.run(["swapon", disk + "1"])
    subprocess.run(["mount", disk + "2", "/mnt"])
