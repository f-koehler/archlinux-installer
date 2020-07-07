from pathlib import Path
from typing import List, Optional, Union

from archinst.block_device import BlockDevice
from archinst.cmd import run


def clear_disk(disk: Union[str, Path], label: str = "gpt"):
    run(["parted", "-s", str(disk), "mklabel", label])


class Partition(BlockDevice):
    def __init__(
        self,
        base_device: Union[str, Path],
        number: int,
        start: str,
        end: str,
        type_: Optional[str] = None,
    ):
        self.base_device = str(base_device)
        super().__init__(self.base_device + str(number))
        self.number = number
        self.start = start
        self.end = end
        self.type_ = type_


class PartitionLayout:
    def __init__(self, path: Union[str, Path], label: str = "gpt"):
        self.path = str(path)
        self.label = label
        self.partitions: List[Partition] = []

    @staticmethod
    def create_empty_gpt(device: Union[str, Path]):
        clear_disk(device)
        return PartitionLayout(device, "gpt")

    def append(self, end: str = "100%", type_: Optional[str] = None):
        if self.partitions:
            start = self.partitions[-1].end
        else:
            start = "0%"

        partition = Partition(self.path, len(self.partitions) + 1, start, end, type_)

        command = [
            "parted",
            "-s",
            "-a",
            "optimal",
            str(self.path),
            "mkpart",
            "primary",
        ]

        if partition.type_ is not None:
            command.append(partition.type_)

        command += [
            partition.start,
            partition.end,
        ]

        run(command)

        self.partitions.append(partition)
        return partition
