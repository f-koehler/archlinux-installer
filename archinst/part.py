from pathlib import Path
from typing import Dict, List, Union

from archinst.cmd import run


def clear_disk(disk: Union[str, Path], label: str = "gpt"):
    run(["parted", "-s", str(disk), "mklabel", label])


class PartitionLayout:
    def __init__(self, label: str = "gpt"):
        self.label = label
        self.partitions: List[Dict[str, str]] = []

    def append(self, type: str, end: str):
        if self.partitions:
            start = self.partitions[-1]["end"]
        else:
            start = "0%"
        self.partitions.append({"start": start, "end": end, "type": type})

    def apply(self, device: Union[str, Path]):
        clear_disk(device, self.label)
        for partition in self.partitions:
            run([
                "parted", "-s", "-a", "optimal",
                str(device), "mkpart", "primary", partition["type"],
                partition["start"], partition["end"]
            ])
