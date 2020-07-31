import re
from pathlib import Path
from typing import List, Union

from archinst.cmd import run_chroot

RE_HOOKS = re.compile(r"^\s*HOOKS\s*=\s*\(([\w\s\n]+)\)", re.MULTILINE)


def mkinitcpio(prefix: Union[str, Path] = "/mnt"):
    run_chroot(["mkinitcpio", "-P"], prefix=prefix)


def read_hooks(prefix: Union[str, Path] = "/mnt") -> List[str]:
    with open(Path(prefix) / "etc" / "mkinitcpio.conf", "r") as fptr:
        config = fptr.read()

    match = RE_HOOKS.search(config)
    if match is None:
        return []

    return match.group(1).split()


def write_hooks(hooks: List[str], prefix: Union[str, Path] = "/mnt"):
    line = "HOOKS=({})".format(" ".join(hooks))
    with open(Path(prefix) / "etc" / "mkinitcpio.conf", "r") as fptr:
        config, num = RE_HOOKS.subn(line, fptr.read())
        if num < 1:
            config += "\n" + line
    with open(Path(prefix) / "etc" / "mkinitcpio.conf", "w") as fptr:
        fptr.write(config)


def insert_hook_after(hooks: List[str], hook: str, after: str):
    if hook == after:
        raise ValueError('cannot insert hook "{}" after itself'.format(hook))
    if after not in hooks:
        raise ValueError('hook "{}" not in hook list'.format(after))
    afterpos = hooks.index(after)
    if hook in hooks:
        if hooks.index(hook) < afterpos:
            raise ValueError(
                'hook "{}" already present but before "{}"'.format(hook, after)
            )
        else:
            return
    hooks.insert(hooks.index(after) + 1, hook)
