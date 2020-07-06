from pathlib import Path
from typing import List, Optional, Union

from archinst.cmd import run


def pacstrap(
    packages: Union[str, List[str]], prefix: Optional[Union[str, Path]] = "/mnt"
):
    if isinstance(packages, str):
        run(["pacstrap", str(prefix), packages])
    else:
        run(["pacstrap", str(prefix)] + packages)
