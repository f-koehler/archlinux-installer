from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from archinst.cmd import run
from archinst.mount import MountEntry, mount_list


def clear_disk(disk: Union[str, Path], label: str = "gpt"):
    run(["parted", "-s", str(disk), "mklabel", label])


class PartitionLayout:
    def __init__(self, label: str = "gpt"):
        self.label = label
        self.partitions: List[Dict[str, Union[str, Any]]] = []

    def append(
        self,
        type: str,
        end: str,
        mount: Optional[Union[str, Tuple[Union[str, Path], List[str]]]] = None,
    ):
        if self.partitions:
            start = self.partitions[-1]["end"]
        else:
            start = "0%"
        self.partitions.append(
            {"start": start, "end": end, "type": type, "mount": mount}
        )

    def apply(self, device: Union[str, Path]):
        clear_disk(device, self.label)
        for partition in self.partitions:
            run(
                [
                    "parted",
                    "-s",
                    "-a",
                    "optimal",
                    str(device),
                    "mkpart",
                    "primary",
                    partition["type"],
                    partition["start"],
                    partition["end"],
                ]
            )

    def mount(self, device: Union[str, Path]):
        mounts: List[MountEntry] = []
        for (number, partition) in enumerate(self.partitions):
            if partition["mount"] is None:
                continue
            if isinstance(partition["mount"], str):
                mounts.append((str(device) + str(number + 1), partition["mount"]))
                continue
            mounts.append(
                (
                    str(device) + str(number + 1),
                    partition["mount"][0],
                    partition["mount"][1],
                )
            )

        return mount_list(mounts)
