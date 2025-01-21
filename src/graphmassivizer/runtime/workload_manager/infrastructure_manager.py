# - Manages the infrastructure, including Task Manager discovery and resource allocation.
# - Uses ZooKeeper to track available Task Managers and their resources.
# - Implements the getMachine method, which selects a suitable Task Manager for execution nodes based on resource availability and location preferences.
# - Reclaims execution units when tasks are finished or datasets are erased.

import threading
import logging
import json
from kazoo.client import KazooClient
from kazoo.protocol.states import WatchedEvent, EventType
from core.descriptors import MachineDescriptor, HardwareDescriptor, HDDDescriptor
import uuid

class InfrastructureManager:
    def __init__(self, workload_manager, zookeeper_host, wm_machine_descriptor, config) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.workload_manager = workload_manager
        self.zookeeper_host = zookeeper_host
        self.wm_machine_descriptor = wm_machine_descriptor
        self.config = config

        self.node_info_lock = threading.Lock()
        self.tm_machine_map = {}
        self.available_execution_units_map = {}
        self.machine_idx = 0

        self.zk = KazooClient(hosts=self.zookeeper_host)
        self.zk.start()

        self.init_zookeeper_directories()

        self.machine_descriptors = {}  # Store MachineDescriptors
        self.store_machine_descriptor()
        self.store_environment_model_in_zookeeper()

        # Watch for changes in task managers
        self.zk.ChildrenWatch('/taskmanagers', self.zookeeper_task_manager_watcher)

        self.input_split_manager = None  # Placeholder for actual implementation

    def init_zookeeper_directories(self) -> None:
        paths = ['/workloadmanager', '/taskmanagers', '/environment']
        for path in paths:
            if not self.zk.exists(path):
                self.zk.create(path)
                self.logger.debug(f"Created Zookeeper path: {path}")

    def store_machine_descriptor(self) -> None:
        data = str(self.wm_machine_descriptor).encode('utf-8')
        wm_path = '/workloadmanager'
        if not self.zk.exists(wm_path):
            self.zk.create(wm_path, data)
        else:
            self.zk.set(wm_path, data)
        self.logger.debug("Stored workload manager machine descriptor in Zookeeper.")

    def update_machine_descriptors(self, machine_info) -> None:
        machine_id = machine_info['uid']
        hardware = HardwareDescriptor(
            cpu_cores=machine_info['cpu_cores'],
            size_of_ram=machine_info['size_of_ram'],
            hdd=HDDDescriptor(size_of_hdd=machine_info['size_of_hdd'])
        )
        machine_descriptor = MachineDescriptor(
            address=machine_info['address'],
            host_name=machine_info['host_name'],
            data_port=machine_info['data_port'],
            control_port=machine_info['control_port'],
            hardware=hardware
        )
        self.machine_descriptors[machine_id] = machine_descriptor
        self.logger.debug(f"Updated machine descriptor for {machine_id}.")

    def serialize_environment_model(self):
        # Convert descriptors to dictionaries
        model_data = json.dumps({
            machine_id: descriptor.to_dict() for machine_id, descriptor in self.machine_descriptors.items()
        })
        return model_data.encode('utf-8')  # Convert to bytes for ZooKeeper

    def store_environment_model_in_zookeeper(self) -> None:
        model_data = self.serialize_environment_model()
        model_path = '/environment/machines'
        if self.zk.exists(model_path):
            self.zk.set(model_path, model_data)
        else:
            self.zk.create(model_path, model_data)
        self.logger.debug("Environment model updated in ZooKeeper.")

    def zookeeper_task_manager_watcher(self, task_manager_nodes) -> None:
        with self.node_info_lock:
            self.logger.debug(f"Task Manager nodes: {task_manager_nodes}")
            # Update machine descriptors based on task manager nodes
            for node in task_manager_nodes:
                node_path = f'/taskmanagers/{node}'
                data, stat = self.zk.get(node_path)
                if data:
                    machine_info = json.loads(data.decode('utf-8'))
                    self.update_machine_descriptors(machine_info)
            self.store_environment_model_in_zookeeper()

    def get_machine(self, location_preference=None):
        with self.node_info_lock:
            worker_machines = list(self.tm_machine_map.values())
            if not worker_machines:
                raise Exception("No available machines.")
            self.machine_idx = (self.machine_idx + 1) % len(worker_machines)
            selected_machine = worker_machines[self.machine_idx]
            self.available_execution_units_map[selected_machine.uid] -= 1
            return selected_machine

    def shutdown_infrastructure_manager(self) -> None:
        self.zk.stop()
        self.logger.info("Shutdown infrastructure manager.")