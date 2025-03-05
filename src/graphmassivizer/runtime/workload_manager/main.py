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
from statemachine import Event, State, StateMachine
from typing import Any, Optional, Type
from hdfs import InsecureClient
from graphmassivizer.runtime.workload_manager.infrastructure_manager import InfrastructureManager
from graphmassivizer.core.descriptors.descriptors import Machine


    
    
    
logging.basicConfig(level=logging.INFO)
    
#     # ----------------------------------------
#     # WORKLOAD MANAGER STATE MACHINE
#     # ----------------------------------------
#     # This is the most basic state machine for the 
#     # Workload Manager I could think of. Has most likely 
#     # to be refined and extended.
# class WorkloadManagerState(StateMachine):
    
#     # STATES
#     # ----------------------------------------
#     # initial
#     CREATED = State(initial=True)
#     # transition 
#     INITIALIZED = State()
#     PARALLELIZED = State()
#     OPTIMIZED = State()
#     GREENIFIED = State()
#     SCHEDULED = State()
#     DEPLOYED = State()
#     RUNNING_PROGRAM = State()
#     RUNNING_ONBOARDING = State()
#     FAILED = State()
#     RECOVER = State()
#     # final
#     CANCELLED = State(final=True)
#     FINISHED = State(final=True)
#     # TRANSITIONS: workflow lifecycle
#     # ----------------------------------------
#     initialize = Event(CREATED.to(INITIALIZED))
#     receive_workflow = Event(INITIALIZED.to(PARALLELIZED))
#     optimize = Event(PARALLELIZED.to(OPTIMIZED))
#     optimization_failed = Event(OPTIMIZED.to(FAILED))
#     greenify = Event(OPTIMIZED.to(GREENIFIED))
#     greenification_failed = Event(GREENIFIED.to(FAILED))
#     schedule = Event(GREENIFIED.to(SCHEDULED))
#     schedule_failed = Event(SCHEDULED.to(FAILED))
#     deploy = Event(SCHEDULED.to(DEPLOYED))
#     deploy_failed = Event(DEPLOYED.to(FAILED))
#     start_execution = Event(INITIALIZED.to(RUNNING_PROGRAM))
#     execution_failed = Event(RUNNING_PROGRAM.to(FAILED))
#     finish = Event(RUNNING_PROGRAM.to(FINISHED))
#     # TRANSITIONS: data onboarding
#     # ----------------------------------------
#     onboard_data = Event(INITIALIZED.to(RUNNING_ONBOARDING))
#     onboarding_failed = Event(RUNNING_ONBOARDING.to(FAILED))
#     # TRANSITIONS: failure
#     # ----------------------------------------
#     recover = Event(FAILED.to(RECOVER))
#     cancel = Event(FAILED.to(CANCELLED))

# class LoggingListener:
#     def __init__(self, logger: logging.Logger) -> None:
#         self.logger = logger
        
#     def after_transition(self, event: Event, state: State) -> None:
#         self.logger.info(f"With event {event} to state {state}")


class WorkloadManager:

    def __init__(self, zookeeper_host, machine, hdfs_client) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        # self.state: WorkloadManagerState = WorkloadManagerState()
        # self.state.add_listener(LoggingListener(self.logger))  # type: ignore
        self.zookeeper_host = zookeeper_host
        self.machine = machine
        self.hdfs = hdfs_client
        self.zk = KazooClient(hosts=self.zookeeper_host)
        self.zk.start()
        self.register_self()
        self.infrastructure_manager = None
        
    # def __enter__(self) -> "WorkloadManager":
    #     self.start()
    #     return self

    # def __exit__(self,
    #              exctype: Optional[Type[BaseException]],
    #              excinst: Optional[BaseException],
    #              exctb: Optional[TracebackType]
    #              ) -> bool:
    #     if self.state.current_state not in {WorkloadManagerState.COMPLETED, WorkloadManagerState.FAILED}:
    #         try:
    #             self.complete()
    #         except Exception as e:
    #             if excinst:
    #                 raise Exception("completion failed, but there was an earlier exception that might have caused this.", [e, excinst])
    #     if excinst:
    #         print("Closing the server, because an Exception was raised")
    #         # by returning False, we indicate that the exception was not handled.
    #         return False
        
    #     print("Server closed")
    #     return True
    
    
    def demo_hdfs_io(self) -> None:
        """Example method: do some reading or writing in HDFS."""
        self.logger.info("WorkloadManager is writing to HDFS for demonstration.")
        data_to_write = b'Hello from WorkloadManager!'
        file_path = '/tmp/workload_manager_hello.txt'
        with self.hdfs.write(file_path, overwrite=True) as writer:
            writer.write(data_to_write)
        self.logger.info(f"Wrote file to HDFS: {file_path}")

        self.logger.info("Reading the same file back from HDFS.")
        with self.hdfs.read(file_path) as reader:
            contents = reader.read()
        self.logger.info(f"Read from HDFS: {contents}")

        
    def register_self(self) -> None: 
        node_path = f'/workloadmanagers/{self.machine.ID}'
        mashine_utf8 = self.machine.to_utf8() 
        if self.zk.exists(node_path):
            self.zk.set(node_path, mashine_utf8)
        else:
            self.zk.create(node_path, mashine_utf8, makepath=True)
        self.logger.info(f"Registered WorkloadManager {self.machine} with ZooKeeper.")




def main() -> None:
    try:
        # Initialize logging using our helper
        logger = logging.getLogger('WorkloadManager')
        zookeeper_host = os.environ.get('ZOOKEEPER_HOST', 'zookeeper:2181')
        
        # HDFS NameNode 
        hdfs_namenode = os.environ.get('HDFS_NAMENODE', 'hdfs://namenode:8020')
        logger.info(f"HDFS_NAMENODE = {hdfs_namenode}")
        hdfs_client = InsecureClient(hdfs_namenode, user='root')

        
        
        machine = Machine.parse_from_env(prefix="WM_")
        workload_manager = WorkloadManager(zookeeper_host, machine, hdfs_client)
        logger.info("I am Workload Manager " + str(machine.ID))
        
        
        
        # Optional: demonstrate HDFS I/O
        workload_manager.demo_hdfs_io()
        
        

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