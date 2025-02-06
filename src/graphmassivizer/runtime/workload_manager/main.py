# - The main class responsible for workload management.
# - Implements IClientWMProtocol and ITM2WMProtocol to handle communication with clients and Task Managers.
# - Manages sessions and topologies submitted by clients.
# - Provides functionalities for dataset management (gather, scatter, erase, assign).
# - Monitors cluster utilization and resource usage.

import os
import logging
import logging.handlers
from kazoo.client import KazooClient
from graphmassivizer.runtime.workload_manager.infrastructure_manager import InfrastructureManager

# def setup_logging():
#     """
#     Sets up the logger for the Workload Manager.
#     This configuration creates two handlers:
#       1. A Console (Stream) Handler for local output.
#       2. A SocketHandler to send logs to a central logging server.
#     """
#     logger = logging.getLogger('WorkloadManager')
#     logger.setLevel(logging.DEBUG)  # Use DEBUG to capture all messages

#     # --- Console Handler: prints logs locally ---
#     console_handler = logging.StreamHandler()
#     console_handler.setLevel(logging.INFO)  # Adjust level as needed
#     console_formatter = logging.Formatter('%(asctime)s %(name)-15s %(levelname)-8s %(message)s')
#     console_handler.setFormatter(console_formatter)
#     logger.addHandler(console_handler)

#     # --- SocketHandler: sends logs to the central logging server ---
#     # Retrieve the logging server host from an environment variable (defaulting to localhost)
#     logging_server_host = os.environ.get('LOGGING_SERVER_HOST', '127.0.0.1')
#     logging_server_port = 9020  # This must match the port on which your central logging server listens
#     try:
#         socket_handler = logging.handlers.SocketHandler(logging_server_host, logging_server_port)
#         socket_handler.setLevel(logging.DEBUG)
#         # No formatter is needed since the handler pickles the LogRecord
#         logger.addHandler(socket_handler)
#     except Exception as e:
#         logger.error("Failed to set up SocketHandler: %s", e)

#     return logger


logging.basicConfig(level=logging.INFO)

def main() -> None:
    try:
        # Initialize logging using our helper
        logger = logging.getLogger('WorkloadManager')
        logger.info("Starting Workload Manager... XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

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