from pathlib import Path
from typing import Union

from archinst.cmd import run_chroot


def set_timezone(name: str = "Europe/Berlin", prefix: Union[Path, str] = "/mnt"):
    src = Path(prefix) / "usr" / "share" / "zoneinfo" / name
    if not src.exists():
        raise RuntimeError("timezone file does not exist: " + str(src))

    dest = Path(prefix) / "etc" / "localtime"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.symlink_to(src)
    run_chroot(["hwclock", "--systohc"])


def enable_ntp():
    run_chroot(["timedatectl", "set-ntp", "true"])
