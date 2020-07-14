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
    cwd: Optional[Union[str, Path]] = None,
):
    extra_flags = []
    if username is not None:
        userspec = username
        if group is not None:
            userspec += ":" + group
        extra_flags += ["-u", userspec]

    sh_cmd = " ".join(command)
    if cwd is not None:
        sh_cmd = "cd " + str(cwd) + "&&" + sh_cmd
    run(
        ["arch-chroot"] + extra_flags + [str(prefix)] + ["sh", "-c", sh_cmd],
        environment,
    )
