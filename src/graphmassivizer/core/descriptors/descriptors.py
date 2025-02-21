from dataclasses import dataclass
import os
import hashlib
import uuid
from abc import ABC, abstractmethod

@dataclass
class MachineDescriptor:
    address: str
    host_name: str
    hardware: str
    cpu_cores: int
    ram_size: int
    hdd: int
    
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
            "descriptor": {
                "address": self.descriptor.address,
                "host_name": self.descriptor.host_name,
                "hardware": self.descriptor.hardware,
                "cpu_cores": self.descriptor.cpu_cores,
                "ram_size": self.descriptor.ram_size,
                "hdd": self.descriptor.hdd
            }
        }
        
    def to_utf8(self) -> bytes:
        return str(self.to_dict()).encode('utf-8')
    
    @staticmethod
    def parse_from_env(prefix: str) -> "Machine":
        return Machine(
            ID=int(os.environ.get("NODE_ID", "-1")),
            descriptor=MachineDescriptor.parse_from_env(prefix)
        )

@dataclass
class BGODescriptor:
    ID: int
    input_path: str
    output_path: str


# missing: steps in between, each adding information

class Descriptor(ABC):

    @abstractmethod
    def to_dict(self) -> dict[str, str]:
        raise NotImplementedError("Subclasses should implement this!")

    def get_id(self) -> str:
        dictionary = self.to_dict()
        sorted_by_values = sorted(dictionary.items(), key=lambda item: item[1])
        sorted_tuples = sorted(sorted_by_values, key=lambda item: item[0])
        return hashlib.md5('-'.join([f"{key}={value}" for key, value in sorted_tuples]).encode()).hexdigest()

    def register_listener(self, listener:):



class MachineDescriptor(Descriptor):
    def __init__(self, address: str, host_name: str, data_port: int, control_port: int, hardware) -> None:
        if data_port < 1024 or data_port > 65535 or control_port < 1024 or control_port > 65535:
            raise ValueError("Port numbers must be between 1024 and 65535")

        self.uid = uuid.uuid4()
        self.address = address
        self.host_name = host_name
        self.data_port = data_port
        self.control_port = control_port
        self.hardware = hardware
        self.data_address = (address, data_port)
        self.control_address = (address, control_port)

    def to_dict(self) -> dict[str, str]:
        return {
            'uid': str(self.uid),
            'address': self.address,
            'host_name': self.host_name,
            'data_port': self.data_port,
            'control_port': self.control_port,
            'hardware': self.hardware.to_dict()
        }

    def __repr__(self) -> str:
        return (f"MachineDescriptor(uid={self.uid}, address={self.address}, host_name={self.host_name}, "
                f"data_port={self.data_port}, control_port={self.control_port}, hardware={self.hardware})")


class HardwareDescriptor(Descriptor):
    def __init__(self, cpu_cores: int, size_of_ram: int, hdd) -> None:
        if cpu_cores < 1:
            raise ValueError("CPU cores must be at least 1")
        if size_of_ram < 1:
            raise ValueError("Size of RAM must be positive")

        self.uid = uuid.uuid4()
        self.cpu_cores = cpu_cores
        self.size_of_ram = size_of_ram
        self.hdd = hdd

    def to_dict(self) -> dict[str, str]:
        return {
            'uid': str(self.uid),
            'cpu_cores': self.cpu_cores,
            'size_of_ram': self.size_of_ram,
            'hdd': self.hdd.to_dict()
        }

    def __repr__(self) -> str:
        return (f"HardwareDescriptor(uid={self.uid}, cpu_cores={self.cpu_cores}, "
                f"size_of_ram={self.size_of_ram}, hdd={self.hdd})")


class HDDDescriptor(Descriptor):
    def __init__(self, size_of_hdd: int) -> None:
        if size_of_hdd < 1024 * 1024 * 1024:
            raise ValueError("Size of HDD must be at least 1 GB")

        self.uid = uuid.uuid4()
        self.size_of_hdd = size_of_hdd

    def to_dict(self) -> dict[str, str]:
        return {
            'uid': str(self.uid),
            'size_of_hdd': self.size_of_hdd
        }

    def __repr__(self) -> str:
        return f"HDDDescriptor(uid={self.uid}, size_of_hdd={self.size_of_hdd})"


class AbstractNodeDescriptor(Descriptor):
    def __init__(self, topology_id: uuid.UUID, task_id: uuid.UUID, task_index: int, name: str, is_re_executable: bool) -> None:
        if task_index < 0:
            raise ValueError("Task index must be non-negative")


@dataclass
class DeploymentDescriptor:
    machine: Machine
    BGO: BGODescriptor
    # state??
