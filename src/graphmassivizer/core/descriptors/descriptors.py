import uuid


class MachineDescriptor:
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


class HardwareDescriptor:
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


class HDDDescriptor:
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


class AbstractNodeDescriptor:
    def __init__(self, topology_id: uuid.UUID, task_id: uuid.UUID, task_index: int, name: str, is_re_executable: bool) -> None:
        if task_index < 0:
            raise ValueError("Task index must be non-negative")

        self.topology_id = topology_id
        self.task_id = task_id
        self.task_index = task_index
        self.name = name
        self.is_re_executable = is_re_executable
        self.machine = None
        self.user_code_classes = []
        self.properties_list = []

    def set_machine_descriptor(self, machine) -> None:
        if machine is None:
            raise ValueError("machine cannot be None")
        if self.machine is not None:
            raise ValueError("machine is already set")

        self.machine = machine

    def get_machine_descriptor(self):
        return self.machine

    def set_user_code_classes(self, user_code_classes) -> None:
        if user_code_classes is None:
            raise ValueError("user_code_classes cannot be None")
        self.user_code_classes = user_code_classes

    def get_user_code_classes(self) -> list:
        return self.user_code_classes

    def __repr__(self) -> str:
        return (f"AbstractNodeDescriptor(topology_id={self.topology_id}, task_id={self.task_id}, "
                f"name={self.name}, machine={self.machine})")
