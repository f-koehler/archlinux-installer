import os
import subprocess
import sys
from pathlib import Path
from typing import Union

from archinst.cmd import run_chroot


def add_group(name: str, prefix: Union[str, Path] = "/mnt"):
    run_chroot(["groupadd", name], prefix=prefix)


def add_normal_user(name: str, prefix: Union[str, Path] = "/mnt"):
    add_group(name, prefix)
    run_chroot(["useradd", "-m", "-g", name, "-G", "users", name], prefix=prefix)


def add_sudoer(username: str, prefix: Union[str, Path] = "/mnt"):
    path = Path(prefix) / "etc" / "sudoers"
    line = username + " ALL=(ALL) ALL\n"

    with open(path, "a") as fptr:
        fptr.write(line)

    os.chown(path, 0, 0)
    os.chmod(path, 0o440)


def set_password(username: str, password: str, prefix: Union[str, Path] = "/mnt"):
    subprocess.Popen(
        ["/usr/bin/arch-chroot", str(prefix), "chpasswd"],
        stderr=sys.stderr,
        stdout=sys.stdout,
        stdin=subprocess.PIPE,
    ).communicate(input="{}:{}".format(username, password).encode())
