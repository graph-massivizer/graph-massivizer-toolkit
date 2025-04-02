# - Manages the infrastructure, including Task Manager discovery and resource allocation.
# - Uses ZooKeeper to track available Task Managers and their resources.
# - Implements the getMachine method, which selects a suitable Task Manager for execution nodes based on resource availability and location preferences.
# - Reclaims execution units when tasks are finished or datasets are erased.

import threading
import logging
import json
from kazoo.client import KazooClient
from kazoo.protocol.states import WatchedEvent, EventType
from graphmassivizer.core.descriptors.descriptors import Machine, MachineDescriptor


class InfrastructureManager:
    def __init__(self, workload_manager) -> None:

        self.logger = logging.getLogger(self.__class__.__name__)
        self.workload_manager = workload_manager
        self.zookeeper_host = workload_manager.zookeeper_host
        self.machine = workload_manager.machine

        self.node_info_lock = threading.Lock()
        self.tm_machine_map = {}
        self.available_execution_units_map = {}
        self.machine_idx = 0

        self.zk = workload_manager.zk

        self.init_zookeeper_directories()

        self.machine_descriptors = {}  # Store MachineDescriptors
        # self.store_machine_descriptor()
        self.register_self()
        self.store_environment_model_in_zookeeper()

        # Watch for changes in task managers
        self.zk.zk.ChildrenWatch('/taskmanagers', self.zookeeper_task_manager_watcher)

        self.input_split_manager = None  # Placeholder for actual implementation

    def print_zookeeper_subtree(self, path: str = "/", indent: int = 0) -> None:
        """
        Recursively print (or log) the ZooKeeper nodes under `path`.
        """
        prefix = "  " * indent  # indentation for visual clarity

        try:
            # Get data and children for the current node
            data, stat = self.zk.zk.get(path)
            children = self.zk.zk.get_children(path)
        except Exception as e:
            self.logger.warning(f"Failed to get info for path '{path}': {e}")
            return

        # Print path and data
        # Note: data is raw bytes. You might want to decode them or just print length.
        data_str = data.decode('utf-8', errors='replace') if data else ""
        node_name = path if path != "" else "/"
        self.logger.info(f"{prefix}{node_name} -> '{data_str}'")

        # Recurse for each child
        for child in children:
            # Construct child path carefully
            # If path == "/", then child_path = "/" + child
            # else child_path = path + "/" + child
            if path == "/":
                child_path = f"/{child}"
            else:
                child_path = f"{path}/{child}"
            self.print_zookeeper_subtree(child_path, indent + 1)

    def init_zookeeper_directories(self) -> None:
        paths = ['/workloadmanager', '/taskmanagers', '/environment']
        for path in paths:
            if not self.zk.zk.exists(path):
                self.zk.zk.create(path)
                self.logger.debug(f"Created Zookeeper path: {path}")


    def register_self(self) -> None:
        node_path = f'/workloadmanager/{self.machine.ID}'
        mashine_utf8 = self.machine.to_utf8()
        if self.zk.zk.exists(node_path):
            self.zk.zk.set(node_path, mashine_utf8)
        else:
            self.zk.zk.create(node_path, mashine_utf8, makepath=True)
        self.logger.info(f"Registered TaskManager {self.machine} with ZooKeeper.")

    def serialize_environment_model(self):
        # Convert descriptors to dictionaries
        model_data = json.dumps({
            machine_id: descriptor.to_dict() for machine_id, descriptor in self.machine_descriptors.items()
        })
        return model_data.encode('utf-8')  # Convert to bytes for ZooKeeper

    def store_environment_model_in_zookeeper(self) -> None:
        model_data = self.serialize_environment_model()
        model_path = '/environment/machines'
        if self.zk.zk.exists(model_path):
            self.zk.zk.set(model_path, model_data)
        else:
            self.zk.zk.create(model_path, model_data)
        self.logger.debug("Environment model updated in ZooKeeper.")

    def zookeeper_task_manager_watcher(self, task_manager_nodes) -> None:
        with self.node_info_lock:
            self.logger.debug(f"Task Manager nodes: {task_manager_nodes}")
            # Update machine descriptors based on task manager nodes
            for node in task_manager_nodes:
                node_path = f'/taskmanagers/{node}'
                data, stat = self.zk.zk.get(node_path)
                # if data:
                #     machine_info = json.loads(data.decode('utf-8'))
                #     self.update_machine_descriptors(machine_info)
            self.store_environment_model_in_zookeeper()

            # NOW: Call the subtree-printing function after each event:
            self.logger.info("ZK tree (all) after update:")
            self.print_zookeeper_subtree("/")

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
