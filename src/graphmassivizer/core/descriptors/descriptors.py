from dataclasses import dataclass
import os
import json
import hashlib
import uuid
from abc import ABC, abstractmethod

from graphmassivizer.core.zookeeper.zookeeper_state_manager import ZookeeperStateManager


class Descriptor(ABC):
    def __init__(self, zk_state_manager: ZookeeperStateManager):
        if not isinstance(zk_state_manager, ZookeeperStateManager):
            raise TypeError("Expected a ZookeeperStateManager instance")
        self.zk_state_manager = zk_state_manager
        self.zk_state_manager.register_descriptor(self)

    def __del__(self):
        self.zk_state_manager.unregister_descriptor(self)

    def to_dict(self) -> dict[str, str]:
        return self.__dict__

    def get_id(self) -> str:
        dictionary = self.to_dict()
        sorted_by_values = sorted(dictionary.items(), key=lambda item: item[1])
        sorted_tuples = sorted(sorted_by_values, key=lambda item: item[0])
        return hashlib.md5('-'.join([f"{key}={value}" for key, value in sorted_tuples]).encode()).hexdigest()

    @abstractmethod
    def get_descriptor_category(self):
        """Subclasses must implement this method"""
        pass

    def register_listener(self, listener):
        return None # TODO: implement



@dataclass
class MachineDescriptor(Descriptor):
    address: str
    host_name: str
    hardware: str
    cpu_cores: int
    ram_size: int
    hdd: int

    def __post_init__(self) -> None:
        if self.cpu_cores < 1:
            raise ValueError("CPU cores must be at least 1")
        if self.ram_size < 1:
            raise ValueError("Size of RAM must be positive")

    def to_dict(self) -> dict[str, str]:
        return {
            "address": self.address,
            "host_name": self.host_name,
            "hardware": self.hardware,
            "cpu_cores": self.cpu_cores,
            "ram_size": self.ram_size,
            "hdd": self.hdd
        }

    def get_descriptor_category(self):
        return "env"

    @staticmethod
    def parse_from_env(prefix: str) -> "MachineDescriptor":
        addr = os.environ.get(prefix + "ADDR", "unknown")
        hostname = os.environ.get(prefix + "HOSTNAME", "unknown")
        hardware = os.environ.get(prefix + "HARDWARE", "unknown")

        # parse numeric fields safely
        cpu_cores = int(os.environ.get(prefix + "CPU_CORES", "1"))
        ram_size = int(os.environ.get(prefix + "RAM_SIZE", "256"))
        hdd_size = int(os.environ.get(prefix + "HDD_SIZE", "10"))

        return MachineDescriptor(
            address=addr,
            host_name=hostname,
            hardware=hardware,
            cpu_cores=cpu_cores,
            ram_size=ram_size,
            hdd=hdd_size
        )


@dataclass
class Machine:
    ID: int
    descriptor: MachineDescriptor

    def to_dict(self) -> dict:
        return {
            "ID": self.ID,
            "descriptor": self.descriptor.to_dict()
        }

    def to_utf8(self) -> bytes:
        return json.dumps(self.to_dict()).encode("utf-8")

    @staticmethod
    def parse_from_env(prefix: str) -> "Machine":
        return Machine(
            ID=int(os.environ.get("NODE_ID", "-1")),
            descriptor=MachineDescriptor.parse_from_env(prefix)
        )

    def get_descriptor_category(self):
        return "env"

@dataclass
class BGODescriptor(Descriptor):
    ID: int
    input_path: str
    output_path: str

    def get_descriptor_category(self):
        return "job"

# missing: steps in between, each adding information

@dataclass
class DeploymentDescriptor(Descriptor):
    machine: Machine
    BGO: BGODescriptor
    # state??

    def to_dict(self) -> dict:
        return {
            "machine": self.machine.to_dict(),
            "bgo": self.BGO.to_dict()
        }

    def get_descriptor_category(self):
        return "deploy"
