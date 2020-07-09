from pathlib import Path
from typing import Union

from archinst import cmd


def enable(service: str, prefix: Union[str, Path] = "/mnt"):
    cmd.run_chroot(["systemctl", "enable", service], prefix=prefix)
