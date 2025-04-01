from dataclasses import dataclass
import os
import json
import hashlib
import uuid
from abc import ABC, abstractmethod

from graphmassivizer.core.zookeeper.zookeeper_state_manager import ZookeeperStateManager
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import hashlib
import os

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
        sorted_by_values = sorted(dictionary.items(), key=lambda item: str(item[1]))  # Ensure all values are str
        sorted_tuples = sorted(sorted_by_values, key=lambda item: item[0])
        return hashlib.md5('-'.join([f"{key}={value}" for key, value in sorted_tuples]).encode()).hexdigest()

    @abstractmethod
    def get_descriptor_category(self):
        """Subclasses must implement this method"""
        pass

    def register_listener(self, listener):
        return None  # TODO: implement


@dataclass
class MachineDescriptor:
    address: str
    host_name: str
    hardware: str
    cpu_cores: int
    ram_size: int
    hdd: int
    zk_state_manager: ZookeeperStateManager = field(init=False)

    def __post_init__(self) -> None:
        if self.cpu_cores < 1:
            raise ValueError("CPU cores must be at least 1")
        if self.ram_size < 1:
            raise ValueError("Size of RAM must be positive")

        super().__init__(self.zk_state_manager)

    def to_dict(self) -> dict[str, str]:
        return {
            "address": self.address,
            "host_name": self.host_name,
            "hardware": self.hardware,
            "cpu_cores": str(self.cpu_cores),
            "ram_size": str(self.ram_size),
            "hdd": str(self.hdd)
        }

    def get_descriptor_category(self):
        return "env"

    @staticmethod
    def parse_from_env(zookeeper_state_manager: ZookeeperStateManager, prefix: str) -> "MachineDescriptor":
        addr = os.environ.get(prefix + "ADDR", "unknown")
        hostname = os.environ.get(prefix + "HOSTNAME", "unknown")
        hardware = os.environ.get(prefix + "HARDWARE", "unknown")

        cpu_cores = int(os.environ.get(prefix + "CPU_CORES", "1"))
        ram_size = int(os.environ.get(prefix + "RAM_SIZE", "256"))
        hdd_size = int(os.environ.get(prefix + "HDD_SIZE", "10"))

        descriptor = MachineDescriptor(
            address=addr,
            host_name=hostname,
            hardware=hardware,
            cpu_cores=cpu_cores,
            ram_size=ram_size,
            hdd=hdd_size
        )
        descriptor.zk_state_manager = zookeeper_state_manager
        super(MachineDescriptor, descriptor).__init__(zookeeper_state_manager)
        return descriptor


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
    def parse_from_env(zookeper_state_manager: ZookeeperStateManager, prefix: str) -> "Machine":
        return Machine(
            ID=int(os.environ.get("NODE_ID", "-1")),
            descriptor=MachineDescriptor.parse_from_env(prefix, zookeper_state_manager),
        )

    def get_descriptor_category(self):
        return "env"

@dataclass
class BGODescriptor(Descriptor):
    ID: int
    input_path: str #TODO replace by ObjectHandle
    output_path: str #TODO replace by ObjectHandle
    zk_state_manager: ZookeeperStateManager = field(init=False)

    def __post_init__(self):
        super().__init__(self.zk_state_manager)  # Initialize superclass

    def get_descriptor_category(self):
        return "job"

    def to_dict(self) -> dict:
        return {
            "ID": self.ID,
            "input_path": self.input_path,
            "output_path": self.output_path,
        }

    def to_utf8(self) -> bytes:
        return json.dumps(self.to_dict()).encode("utf-8")

    @staticmethod
    def create(zk_state_manager: ZookeeperStateManager, ID: int, input_path: str, output_path: str) -> "BGODescriptor":
        instance = BGODescriptor(ID, input_path, output_path)
        instance.zk_state_manager = zk_state_manager  # Ensure proper assignment
        instance.__post_init__()  # Automatically initialize superclass
        return instance

@dataclass
class DeploymentDescriptor(Descriptor):
    machine: MachineDescriptor
    BGO: BGODescriptor
    zk_state_manager: ZookeeperStateManager = field(init=False)

    def __post_init__(self):
        # Ensure the descriptors have the same zk_state_manager
        if self.machine.zk_state_manager != self.BGO.zk_state_manager:
            raise ValueError("Mismatched zk_state_manager instances between descriptors")

        self.zk_state_manager = self.machine.zk_state_manager  # Assign shared zk_state_manager
        super().__init__(self.zk_state_manager)

    def to_dict(self) -> dict:
        return {
            "machine": self.machine.to_dict(),
            "bgo": self.BGO.to_dict()
        }

    def get_descriptor_category(self):
        return "deploy"

    def to_utf8(self) -> bytes:
        return json.dumps(self.to_dict()).encode("utf-8")

    @staticmethod
    def create(zk_state_manager: ZookeeperStateManager, machine: MachineDescriptor,
               BGO: BGODescriptor) -> "DeploymentDescriptor":
        if machine.zk_state_manager != BGO.zk_state_manager:
            raise ValueError("All descriptors must use the same ZookeeperStateManager instance")

        instance = DeploymentDescriptor(machine, BGO)
        instance.zk_state_manager = zk_state_manager  # Assign state manager
        instance.__post_init__()  # Automatically initialize superclass
        return instance

@dataclass
class TaskManagerDescriptor(Descriptor):
    machine: Machine
    zk_state_manager: ZookeeperStateManager = field(init=False)

    def __post_init__(self):
        super().__init__(self.zk_state_manager)  # Initialize superclass

    def get_descriptor_category(self):
        return "taskmanagers"

    def to_dict(self) -> dict:
        return {
            "ID": self.machine.ID,
        }

    def to_utf8(self) -> bytes:
        return json.dumps(self.to_dict()).encode("utf-8")


    @staticmethod
    def create(zk_state_manager: ZookeeperStateManager, machine: Machine) -> "TaskManagerDescriptor":
        instance = TaskManagerDescriptor(machine)
        instance.zk_state_manager = zk_state_manager  # Ensure proper assignment
        instance.__post_init__()  # Automatically initialize superclass
        return instance