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
import pyarrow as pa
import pyarrow.fs as pafs

from graphmassivizer.core.descriptors.descriptors import Machine
from graphmassivizer.core.zookeeper.zookeeper_state_manager import ZookeeperStateManager

logging.basicConfig(level=logging.INFO)


class TaskManager:
    def __init__(self, zookeeper_host, hdfs_filesystem) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.zookeeper_host = zookeeper_host
        self.zk = ZookeeperStateManager(hosts=self.zookeeper_host)
        self.machine = Machine.parse_from_env(self.zk,prefix="TM_")
        self.fs = hdfs_filesystem
        self.register_self()

    def register_self(self) -> None:
        node_path = f'/taskmanagers/{self.machine.ID}'
        mashine_utf8 = self.machine.to_utf8()
        if self.zk.zk.exists(node_path):
            self.zk.zk.set(node_path, mashine_utf8)
        else:
            self.zk.zk.create(node_path, mashine_utf8, makepath=True)
        self.logger.info(f"Registered TaskManager {self.machine} with ZooKeeper.")

    def run(self,alg,args):
        alg(args)

    def demo_hdfs_io(self) -> None:
        file_path = f"/tmp/task_manager_hello_{self.machine.ID}.txt"
        data_to_write = f"Hello from TaskManager {self.machine.ID}!\n".encode("utf-8")

        self.logger.info(f"Writing to HDFS path: {file_path}")

        # If you want to simulate "overwrite", manually delete the existing file first
        # try:
        #     self.fs.delete_file(file_path)
        # except FileNotFoundError:
        #     pass

        # Now just call open_output_stream() without 'overwrite'
        with self.fs.open_output_stream(file_path) as f:
            f.write(data_to_write)

        # self.logger.info(f"Reading the same file back from HDFS.")
        # with self.fs.open_input_stream(file_path) as f:
        #     contents = f.read()

        # self.logger.info(f"Read from HDFS: {contents}")

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





        # PyArrow: parse the host and port from the URI
        # e.g. "hdfs://my-hdfs-host:8020"
        # If the user sets HDFS_NAMENODE = "hdfs://namenode:8020"
        # we can parse the host="namenode", port=8020
        # but let's cheat if it's always in the form hdfs://host:port
        import re
        pattern = r'hdfs://([^:]+):(\d+)'
        match = re.match(pattern, hdfs_namenode)
        if not match:
            raise ValueError(f"Could not parse HDFS_NAMENODE={hdfs_namenode}")
        hdfs_host, hdfs_port = match.groups()
        hdfs_port = int(hdfs_port)

        # Create a PyArrow HadoopFileSystem
        fs = pafs.HadoopFileSystem(host=hdfs_host, port=hdfs_port)

        task_manager = TaskManager(zookeeper_host, fs)
        logger.info("I am Task Manager " + str(task_manager.machine.ID))

        # Optional: demonstrate HDFS I/O
        task_manager.demo_hdfs_io()

        # Keep the Task Manager running
        while True:
            pass
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise e
    finally:
        if 'task_manager' in locals():
            task_manager.shutdown()


if __name__ == '__main__':
    main()
