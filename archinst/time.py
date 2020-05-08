from pathlib import Path

from archinst.cmd import run_chroot


def set_timezone(name: str = "Europe/Berlin"):
    src = Path("/") / "mnt" / "usr" / "share" / "zoneinfo" / name
    dest = Path("/") / "mnt" / "etc" / "localtime"
    dest.symlink_to(src)
    run_chroot(["hwclock", "--systohc"])


def enable_ntp():
    run_chroot(["timedatctl", "set-ntp", "true"])
