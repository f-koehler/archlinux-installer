import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

from archinst.block_device import BlockDevice
from archinst.cmd import run


@contextmanager
def luks_container(block_device: BlockDevice, mapper_name: str, password: str):
    try:
        command = [
            "cryptsetup",
            "-v",
            "luksFormat",
            block_device.path,
            "--type",
            "luks",
            "--key-file",
            "-",
        ]
        subprocess.Popen(
            command, stderr=sys.stderr, stdout=sys.stdout, stdin=subprocess.PIPE
        ).communicate(input=password.encode())

        command = ["cryptsetup", "-v", "open", block_device.path, mapper_name]
        run(command)
        yield BlockDevice(Path("/") / "dev" / "mapper" / mapper_name)
    finally:
        try:
            command = ["cryptsetup", "-v", "close", mapper_name]
        except:
            pass
