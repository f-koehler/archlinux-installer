from pathlib import Path
from typing import Union

from archinst.cmd import run


def run_reflector(country: str = "Germany", prefix: Union[Path, str] = "/mnt"):
    mirrorlist = Path(prefix) / "etc" / "pacman.d" / "mirrorlist"
    mirrorlist.parent.mkdir(parents=True, exist_ok=True)
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
            str(mirrorlist),
        ]
    )
