from dataclasses import dataclass
import os


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
        """
        Reads environment variables with the given prefix (e.g. 'TM_' or 'WM_')
        and returns a MachineDescriptor.
        """
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
