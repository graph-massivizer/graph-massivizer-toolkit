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
    def __init__(self, zookeeper_host, machine, hdfs_client) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.zookeeper_host = zookeeper_host
        self.machine = machine
        self.zk = KazooClient(hosts=self.zookeeper_host)
        self.hdfs_client = hdfs_client
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
        
    def demo_hdfs_io(self) -> None:
            """Example method: do some reading or writing in HDFS."""
            self.logger.info("Attempting to write a small file to HDFS for demonstration.")
            data_to_write = b'Hello from TaskManager!'
            # Choose your path in HDFS
            file_path = '/tmp/task_manager_hello.txt'
            with self.hdfs_client.write(file_path, overwrite=True) as writer:
                writer.write(data_to_write)
            self.logger.info(f"Wrote file to HDFS: {file_path}")

            self.logger.info(f"Attempting to read file back from HDFS: {file_path}")
            with self.hdfs_client.read(file_path) as reader:
                contents = reader.read()
            self.logger.info(f"Read from HDFS: {contents}")

    def shutdown(self) -> None:
        self.zk.stop()
        self.logger.info("Shutdown TaskManager.")


def main() -> None:
    try:
        # Initialize logging using our helper
        logger = logging.getLogger('TaskManager')
        zookeeper_host = os.environ.get('ZOOKEEPER_HOST', 'localhost:2181')
        
        # Retrieve HDFS endpoint from environment
        hdfs_namenode = os.environ.get('HDFS_NAMENODE', 'hdfs://namenode:8020')
        logger.info(f"HDFS_NAMENODE = {hdfs_namenode}")

        # Create HDFS client
        hdfs_client = InsecureClient(hdfs_namenode, user='root')
        
        machine = Machine.parse_from_env(prefix="TM_")
        task_manager = TaskManager(zookeeper_host, machine, hdfs_client)
        logger.info("I am Task Manager " + str(machine.ID))
        
        # Optional: demonstrate HDFS I/O
        task_manager.demo_hdfs_io()
        
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
