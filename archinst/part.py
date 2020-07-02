from pathlib import Path
from typing import List, Optional, Tuple, Union

from archinst.cmd import run


def clear_disk(disk: Union[str, Path], label: str = "gpt"):
    run(["parted", "-s", str(disk), "mklabel", label])


class Partition:
    def __init__(
        self,
        base_device: Union[str, Path],
        number: int,
        start: str,
        end: str,
        type_: str,
    ):
        self.base_device = str(base_device)
        self.device = self.base_device + str(number)
        self.number = number
        self.start = start
        self.end = end
        self.type_ = type_


class PartitionLayout:
    def __init__(self, device: Union[str, Path], label: str = "gpt"):
        self.device = str(device)
        self.label = label
        self.partitions: List[Partition] = []

    @staticmethod
    def create_empty_gpt(device: Union[str, Path]):
        clear_disk(device)
        return PartitionLayout(device, "gpt")

    def append(self, type_: str, end: str = "100%"):
        if self.partitions:
            start = self.partitions[-1].end
        else:
            start = "0%"

        partition = Partition(self.device, len(self.partitions) + 1, start, end, type_)

        run(
            [
                "parted",
                "-s",
                "-a",
                "optimal",
                str(self.device),
                "mkpart",
                "primary",
                partition.type_,
                partition.start,
                partition.end,
            ]
        )

        self.partitions.append(partition)
        return partition
