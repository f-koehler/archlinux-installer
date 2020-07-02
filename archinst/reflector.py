from pathlib import Path

from archinst.cmd import run


def run_reflector(chroot: bool = False, country: str = "Germany"):
    if chroot:
        run(
            [
                "reflector",
                "--age",
                "12",
                "--country",
                country,
                "--protocol",
                "https",
                "--sort",
                "rate",
                "--save",
                "/etc/pacman.d/mirrorlist",
            ]
        )
    else:
        (Path("/") / "mnt" / "etc" / "pacman.d").mkdir(parents=True, exist_ok=True)
        run(
            [
                "reflector",
                "--age",
                "12",
                "--country",
                country,
                "--protocol",
                "https",
                "--sort",
                "rate",
                "--save",
                "/mnt/etc/pacman.d/mirrorlist",
            ]
        )
