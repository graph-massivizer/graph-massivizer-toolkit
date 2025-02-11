from dataclasses import dataclass
import os
import json


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
        return json.dumps(self.to_dict()).encode("utf-8")
    
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


@dataclass
class DeploymentDescriptor:
    machine: Machine
    BGO: BGODescriptor
    # state??
