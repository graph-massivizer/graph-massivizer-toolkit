import socket
from graphmassivizer.core.descriptors.descriptors import MachineDescriptor, HardwareDescriptor, HDDDescriptor


from core.descriptors.descriptors import MachineDescriptor
def create_machine_descriptor(config) -> MachineDescriptor:
    address = socket.gethostbyname(socket.gethostname())
    host_name = socket.gethostname()
    data_port = config.get_int("io.tcp.port", default=5000)
    control_port = config.get_int("io.rpc.port", default=5001)
    cpu_cores = config.get_int("machine.cpu.cores", default=4)
    memory_max = config.get_int("machine.memory.max", default=8 * 1024 * 1024 * 1024)  # 8 GB
    disk_size = config.get_int("machine.disk.size", default=256 * 1024 * 1024 * 1024)  # 256 GB

    # Create HDD Descriptor
    hdd_descriptor = HDDDescriptor(size_of_hdd=disk_size)

    # Create Hardware Descriptor
    hardware_descriptor = HardwareDescriptor(cpu_cores=cpu_cores, size_of_ram=memory_max, hdd=hdd_descriptor)

    # Create Machine Descriptor
    machine_descriptor = MachineDescriptor(address=address, host_name=host_name,
                                           data_port=data_port, control_port=control_port,
                                           hardware=hardware_descriptor)
    return machine_descriptor
