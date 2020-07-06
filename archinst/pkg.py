from typing import List, Union, Optional

from archinst.cmd import run


def pacstrap(
    packages: Union[str, List[str]], prefix: Optional[Union[str, List]] = "/mnt"
):
    if isinstance(packages, str):
        run(["pacstrap", str(prefix), packages])
    else:
        run(["pacstrap", str(prefix)] + packages)
