# - The main class responsible for workload management.
# - Implements IClientWMProtocol and ITM2WMProtocol to handle communication with clients and Task Managers.
# - Manages sessions and topologies submitted by clients.
# - Provides functionalities for dataset management (gather, scatter, erase, assign).
# - Monitors cluster utilization and resource usage.

import os
import json
import logging
import logging.handlers
import re
import pyarrow as pa
import pyarrow.fs as pafs
from functools import reduce
from kazoo.client import KazooClient
from statemachine import Event, State, StateMachine
from typing import Any, Optional, Type
from graphmassivizer.runtime.workload_manager.infrastructure_manager import InfrastructureManager
from graphmassivizer.core.zookeeper.zookeeper_state_manager import ZookeeperStateManager
from graphmassivizer.core.descriptors.descriptors import Machine
from graphmassivizer.core.dataflow.data_manager import DataManager
from graphmassivizer.runtime.workload_manager.parallelizer import Parallelizer
from graphmassivizer.runtime.workload_manager.input.preprocessing import InputPipeline
from graphmassivizer.runtime.workload_manager.optimization_1 import Optimizer_1
from graphmassivizer.runtime.workload_manager.optimization_2 import Optimizer_2
from graphmassivizer.runtime.workload_manager.scheduler import Scheduler
from graphmassivizer.runtime.workload_manager.deployer import Deployer
from graphmassivizer.runtime.workload_manager.execution_controller import ExecutionController
from graphmassivizer.core.zookeeper.zookeeper_state_manager import ZookeeperStateManager


logging.basicConfig(level=logging.INFO)

	 # ----------------------------------------
	 # WORKLOAD MANAGER STATE MACHINE
	 # ----------------------------------------
	 # This is the most basic state machine for the
	 # Workload Manager I could think of. Has most likely
	 # to be refined and extended.
class WorkloadManagerState(StateMachine):

	# STATES
	# ----------------------------------------
	# initial
	CREATED = State(initial=True)
	# transition
	INITIALIZED = State()
	PARALLELIZED = State()
	OPTIMIZED = State()
	GREENIFIED = State()
	SCHEDULED = State()
	DEPLOYED = State()
	RUNNING_PROGRAM = State()
	RUNNING_ONBOARDING = State()
	FAILED = State()
	RECOVER = State()
	# final
	CANCELLED = State(final=True)
	FINISHED = State(final=True)
	# TRANSITIONS: workflow lifecycle
	# ----------------------------------------
	initialize = Event(CREATED.to(INITIALIZED))
	parallize_workflow = Event(INITIALIZED.to(PARALLELIZED))
	optimize = Event(PARALLELIZED.to(OPTIMIZED))
	optimization_failed = Event(OPTIMIZED.to(FAILED))
	greenify = Event(OPTIMIZED.to(GREENIFIED))
	greenification_failed = Event(GREENIFIED.to(FAILED))
	schedule = Event(GREENIFIED.to(SCHEDULED))
	schedule_failed = Event(SCHEDULED.to(FAILED))
	deploy = Event(SCHEDULED.to(DEPLOYED))
	deploy_failed = Event(DEPLOYED.to(FAILED))
	start_execution = Event(INITIALIZED.to(RUNNING_PROGRAM))
	execution_failed = Event(RUNNING_PROGRAM.to(FAILED))
	finish = Event(RUNNING_PROGRAM.to(FINISHED))
	# TRANSITIONS: data onboarding
	# ----------------------------------------
	onboard_data = Event(INITIALIZED.to(RUNNING_ONBOARDING))
	onboarding_failed = Event(RUNNING_ONBOARDING.to(FAILED))
	# TRANSITIONS: failure
	# ----------------------------------------
	recover = Event(FAILED.to(RECOVER))
	cancel = Event(FAILED.to(CANCELLED))

class LoggingListener:
	def __init__(self, logger: logging.Logger) -> None:
		self.logger = logger

	def after_transition(self, event: Event, state: State) -> None:
		self.logger.info(f"With event {event} to state {state}")


class WorkloadManager:

	def __init__(self, zookeeper_host, hdfs_fs) -> None:
		self.logger = logging.getLogger(self.__class__.__name__)
		# self.state: WorkloadManagerState = WorkloadManagerState()
		# self.state.add_listener(LoggingListener(self.logger))  # type: ignore
		self.zookeeper_host = zookeeper_host
		self.fs = hdfs_fs
		self.zk = ZookeeperStateManager(self.zookeeper_host)
		self.machine = Machine.parse_from_env(self.zk,prefix="WM_")
		self.register_self()
		self.infrastructure_manager = InfrastructureManager(workload_manager=self)
		self.dataManager = DataManager('/dm', self.zk)
		self.parallelizer = Parallelizer()
		self.optimizer = Optimizer_1()
		self.greenifier = Optimizer_2()
		self.scheduler = Scheduler()
		self.deployer = Deployer()
		self.execution_manager = ExecutionController()
		self.DAG = None  # Placeholder for the actual DAG
  
	# --- Root
	# ------- Infrastructure
	# ------------ MASHINE I
    # ------------ MASHINE II
    # ------- Environment
    # ------------ WM
    # --------------- recived workflow : false
    # --------------- state : CREATED 
    # ------------ TM I
    # ------------ TM II
    # ------------ TM III  
    
    def zookeeper_task_manager_watcher(self, event: Event) -> None:
    		self.logger.info(f"Task Manager event: {event}")
			# TODO
			# When recived_workflow = true

	def register_self(self) -> None:
		node_path = f'/workloadmanagers/{self.machine.ID}'
		mashine_utf8 = self.machine.to_utf8()
		if self.zk.exists(node_path):
			self.zk.set(node_path, mashine_utf8)
		else:
			self.zk.create(node_path, mashine_utf8, makepath=True)
		self.logger.info(f"Registered WorkloadManager {self.machine} with ZooKeeper.")
  
	def receive_workflow(self):
		self.logger.info(f"Received workflow")
		self.DAG = InputPipeline().getWorkflow()
		self.firstTask = reduce(lambda x,y: y if y[1]['first'] == True else x,self.DAG['nodes'].items(),None)[1]
		self.state.initialize()
  
	def parallelize(self) -> None:
		self.logger.info("Parallelizing workload...")
		dag = Parallelizer.parallelize(self.DAG)
		# TODO change state in Zookeeper
		# --- Root
		# ------- Infrastructure
		# ------------ MASHINE I
    	# ------------ MASHINE II
    	# ------- Environment
    	# ------------ WM
    	# --------------- recived workflow : false
    	# --------------- state : PARALLELIZED 
    	# ------------ TM I
    	# ------------ TM II
    	# ------------ TM III  
		self.state.parallize_workflow()
  
	def optimize(self) -> None:
		self.logger.info("Optimizing workload...")
		optimizer = Optimizer_1()
		optimizer.optimize(self.DAG)
		self.state.optimize()
  
	def greenify(self) -> None:
		self.logger.info("Greenifying workload...")
		optimizer = Optimizer_2()
		optimizer.greenify(self.DAG)
  		# TODO change state in Zookeeper
		self.state.greenify()

	def schedule(self) -> None:
		# TODO REZA: WE SHOULD SCHEDULE THE WORKLOAD HERE
		self.logger.info("Scheduling workload...")
		self.state.schedule()

	def deploy(self) -> None:
		# HERE WE SHOULD MAKE SURE THAT THE WORKLOAD IS DEPLOYED
		self.logger.info("Deploying workload...")
		self.state.deploy()
  
	def execute(self) -> None:
		self.logger.info("Executing workload...")
		self.execution_manager.execute(self.DAG)
		self.state.start_execution()
  
	def demo_hdfs_io(self) -> None:
		file_path = '/tmp/workload_manager_hello.txt'
		data_to_write = b'Hello from WorkloadManager!\n'
		self.logger.info(f"Writing to HDFS path: {file_path}")
		with self.fs.open_output_stream(file_path) as f:
			f.write(data_to_write)
		self.logger.info(f"Reading the same file back from HDFS.")
		with self.fs.open_input_stream(file_path) as f:
			contents = f.read()
			self.logger.info(f"Read from HDFS: {contents}")
  

	# def __enter__(self) -> "WorkloadManager":
	#	 self.start()
	#	 return self

	# def __exit__(self,
	#			  exctype: Optional[Type[BaseException]],
	#			  excinst: Optional[BaseException],
	#			  exctb: Optional[TracebackType]
	#			  ) -> bool:
	#	 if self.state.current_state not in {WorkloadManagerState.COMPLETED, WorkloadManagerState.FAILED}:
	#		 try:
	#			 self.complete()
	#		 except Exception as e:
	#			 if excinst:
	#				 raise Exception("completion failed, but there was an earlier exception that might have caused this.", [e, excinst])
	#	 if excinst:
	#		 print("Closing the server, because an Exception was raised")
	#		 # by returning False, we indicate that the exception was not handled.
	#		 return False

	#	 print("Server closed")
	#	 return True










def main() -> None:
	try:
		# Initialize logging using our helper
		logger = logging.getLogger('WorkloadManager')
		zookeeper_host = os.environ.get('ZOOKEEPER_HOST', 'zookeeper:2181')

		hdfs_namenode = os.environ.get('HDFS_NAMENODE', 'hdfs://namenode:8020')
		logger.info(f"HDFS_NAMENODE = {hdfs_namenode}")

		metaphactory_host = os.environ.get('METAPHACTORY')

		# Parse HDFS host/port from the URI
		pattern = r'hdfs://([^:]+):(\d+)'
		match = re.match(pattern, hdfs_namenode)
		if not match:
			raise ValueError(f"Could not parse HDFS_NAMENODE={hdfs_namenode}")
		hdfs_host, hdfs_port = match.groups()
		hdfs_port = int(hdfs_port)
		fs = pafs.HadoopFileSystem(host=hdfs_host, port=hdfs_port)

		workload_manager = WorkloadManager(zookeeper_host, fs)
		logger.info("I am Workload Manager " + str(workload_manager.machine.ID))
  
  
  
  

		# Optional: demonstrate HDFS I/O
		#workload_manager.demo_hdfs_io()

		# TODO Zookeeper listener for triggering workflow execution

		# The InfrastructureManager will handle storing the environment model into ZooKeeper

		# Keep the main thread alive if necessary
		while True:
			pass  # Replace with actual workload manager logic

	except Exception as e:
		logging.error(f"An error occurred: {e}")
		raise e
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
