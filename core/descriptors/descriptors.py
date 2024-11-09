import uuid
from typing import List, Optional

class MachineDescriptor:
    def __init__(self, address: str, host_name: str, data_port: int, control_port: int, hardware):
        if data_port < 1024 or data_port > 65535 or control_port < 1024 or control_port > 65535:
            raise ValueError("Port numbers must be between 1024 and 65535")
        
        self.uid = uuid.uuid4()
        self.address = address
        self.host_name = host_name
        self.data_port = data_port
        self.control_port = control_port
        self.hardware = hardware

    def __repr__(self):
        return f"MachineDescriptor(uid={self.uid}, address={self.address}, data_port={self.data_port}, control_port={self.control_port}, hardware={self.hardware})"

class HardwareDescriptor:
    def __init__(self, cpu_cores: int, size_of_ram: int, hdd):
        if cpu_cores < 1 or size_of_ram < 1:
            raise ValueError("CPU cores and RAM size must be positive")
        
        self.uid = uuid.uuid4()
        self.cpu_cores = cpu_cores
        self.size_of_ram = size_of_ram
        self.hdd = hdd

    def __repr__(self):
        return f"HardwareDescriptor(uid={self.uid}, cpu_cores={self.cpu_cores}, size_of_ram={self.size_of_ram}, hdd={self.hdd})"

class HDDDescriptor:
    def __init__(self, size_of_hdd: int):
        if size_of_hdd < 1024 * 1024 * 1024:
            raise ValueError("HDD size must be at least 1 GB")
        
        self.uid = uuid.uuid4()
        self.size_of_hdd = size_of_hdd

    def __repr__(self):
        return f"HDDDescriptor(uid={self.uid}, size_of_hdd={self.size_of_hdd})"

class AbstractNodeDescriptor:
    def __init__(self, topology_id: uuid.UUID, task_id: uuid.UUID, task_index: int, name: str, is_re_executable: bool):
        if task_index < 0:
            raise ValueError("Task index must be non-negative")
        
        self.topology_id = topology_id
        self.task_id = task_id
        self.task_index = task_index
        self.name = name
        self.is_re_executable = is_re_executable
        self.machine = None

    def set_machine_descriptor(self, machine: MachineDescriptor):
        if self.machine is not None:
            raise ValueError("Machine descriptor is already set")
        
        self.machine = machine

    def __repr__(self):
        return f"AbstractNodeDescriptor(topology_id={self.topology_id}, task_id={self.task_id}, name={self.name}, machine={self.machine})"

class DeploymentDescriptor:
    def __init__(self, node_descriptor: AbstractNodeDescriptor, input_bindings: List[AbstractNodeDescriptor], output_bindings: List[AbstractNodeDescriptor]):
        self.node_descriptor = node_descriptor
        self.input_bindings = input_bindings
        self.output_bindings = output_bindings

    def __repr__(self):
        return f"DeploymentDescriptor(node_descriptor={self.node_descriptor}, input_bindings={self.input_bindings}, output_bindings={self.output_bindings})"
