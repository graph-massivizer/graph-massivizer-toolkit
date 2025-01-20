# The main class for the Task Manager.
# - Initializes and manages core components like (IOManager), (EventManager), TaskExecutionManager.
# - Connects to ZooKeeper to retrieve the Workload Manager's information.
# - Implements the IWM2TMProtocol to handle communication with the Workload Manager.
# - installTask: Installs and schedules a task (BGOs) received from the Workload Manager.
# - addOutputBinding: Adds output bindings to datasets, specifying how data is transferred to subsequent tasks.
# - getDataset, getMutableDataset: Provides access to datasets managed by the Task Manager.

import os
import json
import logging
import socket
import uuid
from kazoo.client import KazooClient

logging.basicConfig(level=logging.INFO)

class TaskManager:
    def __init__(self, zookeeper_host):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.zookeeper_host = zookeeper_host
        self.zk = KazooClient(hosts=self.zookeeper_host)
        self.zk.start()
        self.register_self()

    def register_self(self):
        machine_info = self.collect_machine_info()
        node_path = f'/taskmanagers/{machine_info["uid"]}'
        data = json.dumps(machine_info).encode('utf-8')
        if self.zk.exists(node_path):
            self.zk.set(node_path, data)
        else:
            self.zk.create(node_path, data, makepath=True)
        self.logger.info(f"Registered TaskManager {machine_info['uid']} with ZooKeeper.")

    def collect_machine_info(self):
        machine_info = {
            'uid': str(uuid.uuid4()),
            'address': socket.gethostbyname(socket.gethostname()),
            'host_name': socket.gethostname(),
            'data_port': 5000,
            'control_port': 5001,
            'cpu_cores': 4,
            'size_of_ram': 8 * 1024 * 1024 * 1024,  # 8 GB
            'size_of_hdd': 256 * 1024 * 1024 * 1024  # 256 GB
        }
        return machine_info

    def shutdown(self):
        self.zk.stop()
        self.logger.info("Shutdown TaskManager.")

def main():
    try:
        zookeeper_host = os.environ.get('ZOOKEEPER_HOST', 'localhost:2181')
        task_manager = TaskManager(zookeeper_host)
        # Keep the Task Manager running
        while True:
            pass
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if 'task_manager' in locals():
            task_manager.shutdown()

if __name__ == '__main__':
    main()