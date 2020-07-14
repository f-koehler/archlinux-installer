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
    sh_command = "su --login --pty"

    if group is not None:
        sh_command += " --group=" + group

    if username is not None:
        sh_command += " " + username

    if cwd is not None:
        sh_command += ' --command "cd {} && {}"'.format(str(cwd), " ".join(command))
    else:
        sh_command += ' --command "{}"'.format(" ".join(command))

    run(["arch-chroot", str(prefix), "sh", "-c", sh_command], environment)
