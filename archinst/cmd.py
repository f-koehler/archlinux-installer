import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union


def run(
    command: List[str],
    environment: Optional[Dict[str, str]] = None,
    cwd: Optional[Union[str, Path]] = None,
):
    env = os.environ.copy()
    if environment:
        for key in environment:
            env[key] = environment[key]
    subprocess.run(command, check=True, env=env, cwd=cwd)


def run_chroot(
    command: List[str],
    environment: Optional[Dict[str, str]] = None,
    prefix: Union[str, Path] = "/mnt",
    username: Optional[str] = None,
    group: Optional[str] = None,
):
    extra = []
    if username is not None:
        extra.append("--userspec=" + username)
        if group is not None:
            extra[0].append(":" + group)
    run(["arch-chroot"] + extra + [str(prefix)] + command, environment)
