# - The main class responsible for workload management.
# - Implements IClientWMProtocol and ITM2WMProtocol to handle communication with clients and Task Managers.
# - Manages sessions and topologies submitted by clients.
# - Provides functionalities for dataset management (gather, scatter, erase, assign).
# - Monitors cluster utilization and resource usage.

import os
import json
import logging
import logging.handlers
from kazoo.client import KazooClient
from graphmassivizer.runtime.workload_manager.infrastructure_manager import InfrastructureManager
from graphmassivizer.core.descriptors.descriptors import Machine

class WorkloadManager:

    def __init__(self, zookeeper_host, machine) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.zookeeper_host = zookeeper_host
        self.machine = machine
        self.zk = KazooClient(hosts=self.zookeeper_host)
        self.zk.start()
        self.register_self()
        
    def register_self(self) -> None: 
        node_path = f'/workloadmanagers/{self.machine.ID}'
        mashine_utf8 = self.machine.to_utf8() 
        if self.zk.exists(node_path):
            self.zk.set(node_path, mashine_utf8)
        else:
            self.zk.create(node_path, mashine_utf8, makepath=True)
        self.logger.info(f"Registered WorkloadManager {self.machine} with ZooKeeper.")


logging.basicConfig(level=logging.INFO)

def main() -> None:
    try:
        # Initialize logging using our helper
        logger = logging.getLogger('WorkloadManager')
        zookeeper_host = os.environ.get('ZOOKEEPER_HOST', 'zookeeper:2181')
        machine = Machine.parse_from_env(prefix="WM_")
        workload_manager = WorkloadManager(zookeeper_host, machine)
        logger.info("I am Workload Manager " + str(machine.ID))

        # Instantiate the InfrastructureManager
        infrastructure_manager = InfrastructureManager(
            workload_manager=workload_manager, 
            zookeeper_host=zookeeper_host,
            machine=machine
        )
        
        # TODO Zookeeper listener for triggering workflow execution

        # The InfrastructureManager will handle storing the environment model into ZooKeeper

        # Keep the main thread alive if necessary
        while True:
            pass  # Replace with actual workload manager logic

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        # Ensure that the infrastructure manager shuts down properly
        if 'infrastructure_manager' in locals():
            infrastructure_manager.shutdown_infrastructure_manager()
            
def execute_dataflow_job(user_defined_json_DAG) -> None:
    
    # TODO Daniel
    
    # Statemachine to manage the lifecycle of the Workload Manager
    
    # Transformation PHASE 1 - 5
    # parallelizer
    # optimization_1
    # optimization_2
    # ??
    # scheduler
    
    
    # Phase 6 EXECUTION
    
    pass

if __name__ == '__main__':
    main()