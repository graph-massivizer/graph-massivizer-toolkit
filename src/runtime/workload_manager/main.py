# - The main class responsible for workload management.
# - Implements IClientWMProtocol and ITM2WMProtocol to handle communication with clients and Task Managers.
# - Manages sessions and topologies submitted by clients.
# - Provides functionalities for dataset management (gather, scatter, erase, assign).
# - Monitors cluster utilization and resource usage.

import os
import logging
from kazoo.client import KazooClient
from infrastructure_manager import InfrastructureManager
from core.descriptors.descriptor_factory import create_machine_descriptor
# Import any necessary configuration classes or functions

logging.basicConfig(level=logging.INFO)

def main() -> None:
    try:
        # Initialize logging
        logger = logging.getLogger('WorkloadManager')
        logger.info("Starting Workload Manager...")

        # Get ZooKeeper host from environment variables
        zookeeper_host = os.environ.get('ZOOKEEPER_HOST', 'zookeeper:2181')

        # Initialize configuration
        config = {}  # Replace with actual configuration if available

        # Create the workload manager's machine descriptor
        wm_machine_descriptor = create_machine_descriptor(config)

        # Instantiate the InfrastructureManager
        infrastructure_manager = InfrastructureManager(
            workload_manager=None,  # Replace with actual workload manager instance if available
            zookeeper_host=zookeeper_host,
            wm_machine_descriptor=wm_machine_descriptor,
            config=config
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