from dataclasses import dataclass


@dataclass
class MachineDescriptor:
    address: str
    host_name: str
    hardware: str
    cpu_cores: int
    ram_size: int
    hdd: int


@dataclass
class Machine:
    ID: int
    descriptor: MachineDescriptor


@dataclass
class BGODescriptor:
    ID: int
    input_path: str
    output_path: str


# missing: steps in between, each adding information


@dataclass
class DeploymentDescriptor:
    machine: Machine
    BGO: BGODescriptor
    # state??
