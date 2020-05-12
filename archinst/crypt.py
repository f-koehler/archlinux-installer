import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Union

from archinst.cmd import run


def create_luks_container(device: Union[str, Path], password: str):
    command = [
        "cryptsetup", "-v", "luksFormat",
        str(device), "--type", "luks", "--cipher", "aes-xts-plain64",
        "--key-size", "512", "--hash", "sha256", "--iter-time", "5000",
        "--use-urandom", "--key-file", "-"
    ]
    process = subprocess.Popen(command,
                               stderr=sys.stderr,
                               stdout=sys.stdout,
                               stdin=subprocess.PIPE)
    process.communicate(input=password.encode())


def create_plain_container(device: Union[str, Path], password: str):
    command = [
        "cryptsetup", "-v", "luksFormat",
        str(device), "--type", "plain", "--cipher", "aes-xts-plain64",
        "--key-size", "512", "--key-file", "-"
    ]
    process = subprocess.Popen(command,
                               stderr=sys.stderr,
                               stdout=sys.stdout,
                               stdin=subprocess.PIPE)
    process.communicate(input=password.encode())


def open_luks_container(device: Union[str, Path], mapper_name: str,
                        password: str):
    command = [
        "cryptsetup", "-v", "open",
        str(device), mapper_name, "--type", "luks", "--key-file", "-"
    ]
    process = subprocess.Popen(command,
                               stderr=sys.stderr,
                               stdout=sys.stdout,
                               stdin=subprocess.PIPE)
    process.communicate(input=password.encode())


def open_plain_container(device: Union[str, Path], mapper_name: str,
                         password: str):
    command = [
        "cryptsetup", "-v", "open",
        str(device), mapper_name, "--type", "plain", "--key-file", "-"
    ]
    process = subprocess.Popen(command,
                               stderr=sys.stderr,
                               stdout=sys.stdout,
                               stdin=subprocess.PIPE)
    process.communicate(input=password.encode())


def close_crypt(mapper_name: str):
    run(["cryptsetup", "close", mapper_name])


@contextmanager
def luks_container(device: Union[str, Path], mapper_name: str, password: str):
    try:
        open_luks_container(device, mapper_name, password)
        yield
    finally:
        close_crypt(mapper_name)


@contextmanager
def plain_container(device: Union[str, Path], mapper_name: str, password: str):
    try:
        open_plain_container(device, mapper_name, password)
        yield
    finally:
        close_crypt(mapper_name)
