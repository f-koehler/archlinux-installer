from contextlib import contextmanager
from pathlib import Path
from typing import Union

from archinst.cmd import run


@contextmanager
def luks_container(device: Union[str, Path], mapper_name: str, password: str):
    try:
        command = [
            "cryptsetup",
            "-v",
            "luksFormat",
            str(device),
            "--type",
            "luks",
            "--key-file",
            "-",
        ]
        run(command)

        command = ["cryptsetup", "-v", "open", str(device), mapper_name]
        run(command)
        yield
    finally:
        try:
            command = ["cryptsetup", "-v", "close", mapper_name]
        except:
            pass
