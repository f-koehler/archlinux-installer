from typing import List, Union

from archinst.cmd import run


def pacstrap(packages: Union[str, List[str]]):
    if isinstance(packages, str):
        run(["pacstrap", "/mnt", packages])
    else:
        run(["pacstrap", "/mnt"] + packages)
