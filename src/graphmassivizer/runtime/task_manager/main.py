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
from hdfs import InsecureClient

from graphmassivizer.core.descriptors.descriptors import Machine

logging.basicConfig(level=logging.INFO)


class TaskManager:
    def __init__(self, zookeeper_host, machine) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.zookeeper_host = zookeeper_host
        self.machine = machine
        self.zk = KazooClient(hosts=self.zookeeper_host)
        self.zk.start()
        self.register_self()

    def register_self(self) -> None: 
        node_path = f'/taskmanagers/{self.machine.ID}'
        mashine_utf8 = self.machine.to_utf8()
        if self.zk.exists(node_path):
            self.zk.set(node_path, mashine_utf8)
        else:
            self.zk.create(node_path, mashine_utf8, makepath=True)
        self.logger.info(f"Registered TaskManager {self.machine} with ZooKeeper.")

    def shutdown(self) -> None:
        self.zk.stop()
        self.logger.info("Shutdown TaskManager.")


def main() -> None:
    try:
        # Initialize logging using our helper
        logger = logging.getLogger('TaskManager')
        zookeeper_host = os.environ.get('ZOOKEEPER_HOST', 'localhost:2181')
        machine = Machine.parse_from_env(prefix="TM_")
        task_manager = TaskManager(zookeeper_host, machine)
        logger.info("I am Task Manager " + str(machine.ID))
        
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
