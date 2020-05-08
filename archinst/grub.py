from pathlib import Path
from typing import Union

from archinst.cmd import run_chroot
from archinst.pkg import pacstrap


def install_grub_bios(disk: Union[str, Path]):
    pacstrap(["grub", "os-prober", "ntfs-3g"])
    run_chroot(["grub-install", "--target=i386-pc", str(disk)])
    run_chroot(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"])
