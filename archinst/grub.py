import re
from pathlib import Path
from typing import List, Union

from archinst.cmd import run_chroot
from archinst.pkg import pacstrap
from archinst import log


LOGGER = log.get_logger(__name__)
RE_KERNEL_PARAMETERS = re.compile(r"^GRUB_CMDLINE_LINUX_DEFAULT=\"(.+)\"$")


def install_grub_bios(disk: Union[str, Path]):
    pacstrap(["grub", "os-prober", "ntfs-3g"])
    run_chroot(["grub-install", "--target=i386-pc", str(disk)])
    run_chroot(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"])


def install_grub_efi(prefix: Union[str, Path] = "/mnt"):
    pacstrap(["grub", "os-prober", "ntfs-3g", "efibootmgr"], prefix=prefix)
    run_chroot(
        [
            "grub-install",
            "--target=x86_64-efi",
            "--efi-directory=/boot/efi",
            "--bootloader-id=ARCHGRUB",
        ],
        prefix=prefix,
    )
    run_chroot(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"], prefix=prefix)


def read_kernel_parameters(prefix: Union[str, Path] = "/mnt") -> List[str]:
    with open(Path(prefix) / "etc" / "default" / "grub", "r") as fptr:
        config = fptr.read()

    match = RE_KERNEL_PARAMETERS.search(config)
    if match is None:
        return []

    return match.group(1).split()


def remove_matching_kernel_parameters(
    parameters: List[str], pattern: Union[str, re.Pattern]
):
    if isinstance(pattern, re.Pattern):
        regex = pattern
    else:
        regex = re.compile(pattern)

    new_parameters = []
    for parameter in parameters:
        if not regex.match(parameter):
            new_parameters.append(parameter)
    parameters = new_parameters


def write_kernel_parameters(parameters: List[str], prefix: Union[str, Path] = "/mnt"):
    new_line = 'GRUB_CMDLINE_LINUX_DEFAULT="{}"\n'.format(" ".join(parameters))

    with open(Path(prefix) / "etc" / "default" / "grub", "r") as fptr:
        new_config = []
        replaced = False
        for line in fptr:
            if RE_KERNEL_PARAMETERS.match(line):
                new_config.append(new_line)
                replaced = True
            else:
                new_config.append(line)

        if not replaced:
            LOGGER.warn("did not find kernel parameter line in grub config, append it")
            new_config.append(new_line)

    with open(Path(prefix) / "etc" / "default" / "grub", "w") as fptr:
        fptr.writelines(new_config)
        LOGGER.info("wrote the following kernel parameters: %s", str(parameters))
