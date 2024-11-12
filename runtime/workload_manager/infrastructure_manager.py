# - Manages the infrastructure, including Task Manager discovery and resource allocation.
# - Uses ZooKeeper to track available Task Managers and their resources.
# - Implements the getMachine method, which selects a suitable Task Manager for execution nodes based on resource availability and location preferences.
# - Reclaims execution units when tasks are finished or datasets are erased.

import threading
import logging
from kazoo.client import KazooClient
from kazoo.protocol.states import WatchedEvent, EventType
from core.descriptors import MachineDescriptor
import uuid

class InfrastructureManager:
    def __init__(self, workload_manager, zookeeper_host, wm_machine_descriptor, config):
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

        # Initialize Zookeeper directories
        self.init_zookeeper_directories()

        # Store the workload manager machine descriptor in Zookeeper
        self.store_machine_descriptor()

        # Get existing TaskManager nodes and watch for changes
        self.zk.DataWatch('/taskmanagers', self.zookeeper_task_manager_watcher)

        # Initialize the input split manager (not implemented here)
        self.input_split_manager = None  # Placeholder for actual implementation

    def init_zookeeper_directories(self):
        # Ensure that the necessary Zookeeper directories exist
        paths = ['/workloadmanager', '/taskmanagers']
        for path in paths:
            if not self.zk.exists(path):
                self.zk.create(path)
                self.logger.debug(f"Created Zookeeper path: {path}")

    def store_machine_descriptor(self):
        # Serialize the machine descriptor and store it in Zookeeper
        data = str(self.wm_machine_descriptor).encode('utf-8')
        wm_path = '/workloadmanager'
        if not self.zk.exists(wm_path):
            self.zk.create(wm_path, data)
        else:
            self.zk.set(wm_path, data)
        self.logger.debug("Stored workload manager machine descriptor in Zookeeper.")

    def zookeeper_task_manager_watcher(self, data, stat, event):
        if event is not None and event.type == EventType.CHILD:
            self.logger.debug(f"Received Zookeeper event: {event}")
            with self.node_info_lock:
                # Fetch current task managers
                task_manager_nodes = self.zk.get_children('/taskmanagers')

                # Update tm_machine_map and available_execution_units_map accordingly
                # For simplicity, we'll just log the changes
                self.logger.debug(f"Task Manager nodes: {task_manager_nodes}")
                # Implementation of adding/removing machines goes here

    def get_machine(self, location_preference=None):
        with self.node_info_lock:
            worker_machines = list(self.tm_machine_map.values())
            # Implement logic to select a machine based on location preference and availability
            # For now, return a machine in round-robin fashion
            if not worker_machines:
                raise Exception("No available machines.")
            self.machine_idx = (self.machine_idx + 1) % len(worker_machines)
            selected_machine = worker_machines[self.machine_idx]
            # Update available execution units
            self.available_execution_units_map[selected_machine.uid] -= 1
            return selected_machine

    def shutdown_infrastructure_manager(self):
        self.zk.stop()
        self.logger.info("Shutdown infrastructure manager.")

    # Additional methods to implement:
    # - reclaim_execution_units
    # - register_hdfs_source
    # - get_next_input_split_for_hdfs_source
    # - get_number_of_machines
    # - get_machines_with_input_split
    # These methods depend on your specific implementation details.