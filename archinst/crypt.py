import subprocess
from pathlib import Path
from typing import Union


def create_luks_container(device: Union[str, Path], password: str):
    command = [
        "cryptsetup", "-v", "luksFormat",
        str(device), "--type", "luks", "--cipher", "aes-xts-plain64",
        "--key-size", "512", "--hash", "sha256", "--iter-time", "5000",
        "--use-urandom", "--keyfile", "-"
    ]
    subprocess.run(command, check=True, stdin=password.encode())
