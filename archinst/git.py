from pathlib import Path
from typing import Union

from archinst.cmd import run


def clone(url: str, dest: Union[Path, str]):
    Path(dest).mkdir(parents=True, exist_ok=True)
    run(
        ["git", "clone", url, str(dest)],
        {
            "GIT_SSH_COMMAND": "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
        },
    )
