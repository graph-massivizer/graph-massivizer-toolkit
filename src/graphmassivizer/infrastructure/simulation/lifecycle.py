import logging
import socket
import time
from types import TracebackType
from typing import Any, Optional, Type
from statemachine import Event, State, StateMachine
import docker
from functools import reduce,partial
import pyarrow.fs as pafs
import pyarrow as pa
import inspect
import json
import pickle
from concurrent.futures import ThreadPoolExecutor

from graphmassivizer.core.descriptors.descriptors import (Machine, MachineDescriptor,SimulationMachineDescriptor)
from graphmassivizer.infrastructure.simulation.cluster import Cluster
from graphmassivizer.infrastructure.simulation.node import (TaskManagerNode, WorkflowManagerNode, ZookeeperNode, HDFSNode, HDFSDataNode, DashboardNode)
from graphmassivizer.runtime.workload_manager.input.preprocessing import InputPipeline
from graphmassivizer.runtime.workload_manager.input.userInputHandler import UserInputHandler
from graphmassivizer.runtime.workload_manager.parallelizer import Parallelizer
from graphmassivizer.runtime.workload_manager.optimization_1 import Optimizer_1
from graphmassivizer.runtime.workload_manager.optimization_2 import Optimizer_2
from graphmassivizer.core.zookeeper.zookeeper_state_manager import ZookeeperStateManager

class LifecycleState(StateMachine):

	CREATED = State(initial=True)
	INITIALIZED = State()
	INPUT_RECEIVED = State()
	PARALLELIZED = State()
	OPTIMIZED = State()
	GREENIFIED = State()
	RUNNING = State()
	FAILED = State(final=True)
	COMPLETED = State(final=True)

	initialize = Event(CREATED.to(INITIALIZED))
	get_input = Event(INITIALIZED.to(INPUT_RECEIVED))
	parallelize = Event(INPUT_RECEIVED.to(PARALLELIZED))
	optimize = Event(PARALLELIZED.to(OPTIMIZED))
	greenify = Event(OPTIMIZED.to(GREENIFIED))
	run = Event(GREENIFIED.to(RUNNING))
	fail = Event(RUNNING.to(FAILED))
	complete = Event(RUNNING.to(COMPLETED))


class LoggingListener:
	def __init__(self, logger: logging.Logger) -> None:
		self.logger = logger

	def after_transition(self, event: Event, state: State) -> None:
		self.logger.info(f"With event {event} to state {state}")


def is_container_running(container_name: str) -> Optional[bool]:
	"""Verify the status of a container by it's name

	:param container_name: the name of the container
	:return: boolean or None
	"""
	RUNNING = "running"
	# Connect to Docker using the default socket or the configuration
	# in your environment
	docker_client = docker.from_env()
	# Or give configuration
	# docker_socket = "unix://var/run/docker.sock"
	# docker_client = docker.DockerClient(docker_socket)

	try:
		container = docker_client.containers.get(container_name)
	except docker.errors.NotFound as exc:
		print(f"Check container name!\n{exc.explanation}")
	else:
		container_state = container.attrs["State"]
		return container_state["Status"] == RUNNING

def executeFunctionsInParallel(functions):
	with ThreadPoolExecutor(max_workers=len(functions)) as executor:
		for func in functions:
			executor.submit(func)
		executor.shutdown(wait=True)

class Simulation:

	def __init__(self) -> None:
		self.logger = logging.getLogger(self.__class__.__name__)
		self.logger.setLevel(logging.INFO)
		self.state: LifecycleState = LifecycleState()
		self.state.add_listener(LoggingListener(self.logger))  # type: ignore
		self.__machine_descriptor = SimulationMachineDescriptor(
			address="",
			host_name=socket.gethostname(),
			hardware="simulated",
			cpu_cores=2,
			ram_size=256,
			hdd=12
		)
		self.__network_name = 'graphmassivizer_simulation_net'
		self.initNumberOfTms = 6

	def __enter__(self) -> "Simulation":
		self.start()
		return self

	def __exit__(self,
				 exctype: Optional[Type[BaseException]],
				 excinst: Optional[BaseException],
				 exctb: Optional[TracebackType] ) -> bool:

		if self.state.current_state not in {LifecycleState.COMPLETED, LifecycleState.FAILED}:
			try:
				self.complete()
			except Exception as e:
				if excinst:
					raise Exception(
						"completion failed, but there was an earlier exception that might have caused this.", [e, excinst])
		if excinst:
			print("Closing the server, because an Exception was raised")
			# by returning False, we indicate that the exception was not handled.
			return False
		print("Server closed")
		return True

	def start(self) -> None:

		# We attempt to change the state ahead of doing the action, it will trigger an exception if this is not possible now.
		# TODO consider using the state transition as a trigger to execute the logic.
		self.state.initialize()

		try:

			# create zookeeper
			zookeeper = ZookeeperNode(Machine(0, self.__machine_descriptor), self.__network_name)

			workflow_manager = WorkflowManagerNode(Machine(1, self.__machine_descriptor), self.__network_name)

			hdfs_node = HDFSNode(Machine(2, self.__machine_descriptor), self.__network_name)

			hdfs_data_node = HDFSDataNode(Machine(2, self.__machine_descriptor), self.__network_name)

			# adding the task managers
			task_managers: list[TaskManagerNode] = []
			offset = 3
			for i in range(self.initNumberOfTms):
				self.logger.info(f"Creating task manager {offset+i}")
				tm = TaskManagerNode(Machine(offset + i, self.__machine_descriptor), self.__network_name)
				task_managers.append(tm)

			# adding dashboard node
			dashboard = DashboardNode(Machine(len(task_managers) + offset, self.__machine_descriptor), self.__network_name)

			# COMMENTED OUT UNTIL READY STATES ARE DEFINED FOR ALL NODES
			# self.waitForNodesToBeReady(zookeeper,hdfs_node,hdfs_data_node,workflow_manager,task_managers,dashboard,TIMEOUT_SECONDS=10000)

			self.cluster = Cluster(
				zookeeper,
				workflow_manager,
				task_managers,
				dashboard,
				self.__network_name,
				hdfs_node,
				[hdfs_data_node])

		except Exception as e:
			self.state.fail()
			raise e

		try:
			self.cluster.ensure_network()

			self.logger.info("deploying all containers")
			zookeeper.deploy()
			self.logger.info("Zookeeper deployed")
			zookeeper.wait_for_zookeeper(10)
			self.logger.info("Zookeeper ready")

			# 3. Deploy the HDFS node
			self.logger.info("Deploying HDFS node...")
			hdfs_node.deploy()
			#hdfs_node.wait_for_hdfs(timeout=20000)

			# 3. Deploy the HDFS node
			self.logger.info("Deploying HDFS data node...")
			hdfs_data_node.deploy()

			workflow_manager.deploy()
			self.logger.info("Workflow Manager started")

			for task_manager in task_managers:
				task_manager.deploy()
				self.logger.info(f"Task Manager started on Node {task_manager.node_id}")

			dashboard.deploy()
			self.logger.info("Dashboard started")

			hdfs_node.wait_for_hdfs(timeout=10000)
			#hdfs_node.create_hdfs_directory("/tmp")
			self.logger.info("HDFS is ready")

		except Exception:
			self.fail()
			raise

		self.logger.info("Full simulation is running...")

	def waitForNodesToBeReady(self,zookeeper,hdfs_node,hdfs_data_node,workflow_manager,task_managers,dashboard,TIMEOUT_SECONDS=None):  # None timeout means there is no limit, otherwise timeout after TIMEOUT_SECONDS seconds
		executeFunctionsInParallel([self.waitForZookeeper(TIMEOUT_SECONDS,zookeeper),
									self.waitForHDFSName(TIMEOUT_SECONDS,hdfs_node),
									self.waitForHDFSData(TIMEOUT_SECONDS,hdfs_data_node),
									self.waitForWM(TIMEOUT_SECONDS,workflow_manager),
									self.waitForTMs(TIMEOUT_SECONDS,task_managers),
									self.waitForDash(TIMEOUT_SECONDS,dashboard)])
		self.logger.info("All nodes ready")

	def waitForZookeeper(self,TIMEOUT_SECONDS,zookeeper):
		if not zookeeper.status.ready_event.wait(TIMEOUT_SECONDS):
			raise TimeoutError(f"Ready signal from Zookeeper node timed out after {TIMEOUT_SECONDS} seconds")

	def waitForWM(self,TIMEOUT_SECONDS,workflow_manager):
		if not workflow_manager.status.ready_event.wait(TIMEOUT_SECONDS):
			raise TimeoutError(f"Ready signal from workflow manager node timed out after {TIMEOUT_SECONDS} seconds")

	def waitForTMs(self,TIMEOUT_SECONDS,task_managers):
		executeFunctionsInParallel(list(map(partial(self.waitForTM,TIMEOUT_SECONDS),task_managers)))

	def waitForTM(self,TIMEOUT_SECONDS,task_manager):
		if not task_manager.status.ready_event.wait(TIMEOUT_SECONDS):
			raise TimeoutError(f"Ready signal from task manager node {task_manager.machine.ID} timed out after {TIMEOUT_SECONDS} seconds")

	def waitForHDFSName(self,TIMEOUT_SECONDS,hdfs_node):
		if not hdfs_node.status.ready_event.wait(TIMEOUT_SECONDS):
			raise TimeoutError(f"Ready signal from hdfs node timed out after {TIMEOUT_SECONDS} seconds")

	def waitForHDFSData(self,TIMEOUT_SECONDS,hdfs_data_node):
		if not hdfs_data_node.status.ready_event.wait(TIMEOUT_SECONDS):
			raise TimeoutError(f"Ready signal from hdfs data node timed out after {TIMEOUT_SECONDS} seconds")

	def waitForDash(self,TIMEOUT_SECONDS,dashboard):
		if not dashboard.status.ready_event.wait(TIMEOUT_SECONDS):
			raise TimeoutError(f"Ready signal from dashboard node timed out after {TIMEOUT_SECONDS} seconds")

	def fail(self) -> None:
		self._try_complete_nodes()
		self.cluster.remove_network()
		if self.state.current_state != LifecycleState.FAILED:
			self.state.fail()

	def complete(self) -> None:
		self.logger.info("Completing the simulation")
		self._try_complete_nodes()
		self.cluster.remove_network()
		if (self.state.current_state != LifecycleState.FAILED):
			self.state.complete()

	def run_default_input_pipeline(self):
		self.get_input()
		self.parallelize()
		self.optimize()
		self.greenify()
		self.run()
		self.complete()

	def get_input(self) -> None:
		self.DAG = InputPipeline().getWorkflow()
		self.firstTask = reduce(lambda x,y: y if y[1]['first'] == True else x,self.DAG['nodes'].items(),None)[1]
		self.state.get_input()

	def parallelize(self) -> None:
		Parallelizer.parallelize(self.DAG)
		self.state.parallelize()

	def optimize(self) -> None:
		Optimizer_1.optimize(self.DAG)
		self.state.optimize()

	def greenify(self) -> None:
		Optimizer_2.optimize(self.DAG)
		self.state.greenify()

	def run(self) -> None:
		self.state.run()
		task = self.firstTask
		args = self.DAG['args']
		i = 0
		while task:
			algorithm = list(task['implementations'].values())[0]['class'].run
			self.cluster.task_managers[i].run(algorithm,args)
			task = self.DAG['nodes'][list(task['next'])[0]] if task and 'next' in task else None
			i += 1

	def wait_for_completion(self) -> None:
		raise NotImplementedError()

	def _complete_tms(self):
		for tm in self.cluster.task_managers:
			try:
				tm.logger.setLevel(logging.ERROR) # Currently zookeeper throws a thousand warnings as soon as you shut things off
				tm.shutdown()
				self.logger.info(
					f"Task manager {tm.node_id} has been shut down.")
			except Exception as e:
				self.logger.info(
					f"Closing the task manager {tm.node_id} failed. " + str(e))
				self.state.fail()

	def _complete_wm(self):
		try:
			self.cluster.workload_manager.logger.setLevel(logging.ERROR) # Currently zookeeper throws a thousand warnings as soon as you shut things off
			self.cluster.workload_manager.shutdown()
			self.logger.info("Workload manager stopped")
		except Exception as e:
			self.logger.info("Closing the workload manager failed. " + str(e))
			self.state.fail()

	def _complete_zk(self):
		try:
			self.cluster.zookeeper.logger.setLevel(logging.ERROR) # Currently zookeeper throws a thousand warnings as soon as you shut things off
			self.cluster.zookeeper.shutdown()
			self.logger.info("Zookeeper stopped")
		except Exception as e:
			self.logger.info("Closing the zookeeper failed. " + str(e))
			self.state.fail()

	def _complete_hdfs(self):
		try:
			for dataNode in self.cluster.hdfs_data_nodes:
				dataNode.logger.setLevel(logging.ERROR) # Currently zookeeper throws a thousand warnings as soon as you shut things off
				dataNode.shutdown()
				self.logger.info("HDFS Data Node stopped")
			self.cluster.hdfs_node.logger.setLevel(logging.ERROR) # Currently zookeeper throws a thousand warnings as soon as you shut things off
			self.cluster.hdfs_node.shutdown()
			self.logger.info("HDFS Name Node stopped")
		except Exception as e:
			self.logger.info("Closing the hdfs failed. " + str(e))
			self.state.fail()

	def _complete_dash(self):
		try:
			self.cluster.dashboard.logger.setLevel(logging.ERROR) # Currently zookeeper throws a thousand warnings as soon as you shut things off
			self.cluster.dashboard.shutdown()
			self.logger.info("Dashboard stopped")
		except Exception as e:
			self.logger.info("Closing the dashboard failed. " + str(e))
			self.state.fail()

	def _try_complete_nodes(self):
		executeFunctionsInParallel([self._complete_tms,self._complete_wm,self._complete_zk,self._complete_hdfs,self._complete_dash])

	def get_status(self) -> tuple[str, list[dict[str, Any]]]:
		# Collect status from the cluster and nodes
		status: tuple[str, list[dict[str, Any]]] = (
			self.state.current_state.id,
			[]
		)
		if self.state.current_state in {LifecycleState.CREATED, LifecycleState.RUNNING}:

			for tm in self.cluster.task_managers:
				node_status: dict[str, Any] = tm.report_status()
				status[1].append(node_status)
		return status
