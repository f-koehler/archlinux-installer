import subprocess
from pathlib import Path
from typing import List, Union


def run(command: List[str]):
    subprocess.run(command, check=True)


def run_chroot(command: List[str], root: Union[str, Path] = "/mnt"):
    run(["arch-chroot", str(root)] + command)
