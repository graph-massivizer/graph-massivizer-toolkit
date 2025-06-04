import logging
import math
import time
import threading
import io
import os,re
from threading import Thread
from abc import abstractmethod
from typing import Any, Optional

import pyarrow as pa
import pyarrow.fs as pafs

import docker
from docker.models.containers import Container

from graphmassivizer.core.descriptors.descriptors import Machine, MachineDescriptor
from graphmassivizer.infrastructure.components import Node, NodeStatus
from graphmassivizer.runtime.task_manager.main import TaskManager
import inspect

def get_fs(node):

	pattern = r'hdfs://([^:]+):(\d+)'
	match = re.match(pattern, node)
	if not match:
		raise ValueError(f"Could not parse HDFS_NAMENODE={node}")
	hdfs_host, hdfs_port = match.groups()
	hdfs_port = int(hdfs_port)

	# Create a PyArrow HadoopFileSystem
	return pafs.HadoopFileSystem(host=hdfs_host, port=hdfs_port)

# ----------------------------------------
# SIMULATED NODE
# ----------------------------------------
class SimulatedNode(Node, Thread):
	def __init__(self,
				 machine: Machine,
				 docker_network_name: str,
				 container_name: str,
				 image_name: str,
				 tag: str,
				 ports: dict[str, int | list[int]],
				 command: Optional[str] = None
				 ) -> None:
		"""network must be of type graphmassivizer.infrastructure.simulation.network import Network
		but we have a cyclic import left
		"""
		super().__init__(node_id=machine.ID)
		Thread.__init__(self)
		self.docker_client = docker.from_env()
		self.docker_container: Optional[Container] = None
		self.machine_descriptor: MachineDescriptor = machine.descriptor
		self.docker_network_name = docker_network_name

		self.__container_name = container_name
		self.__image_name = image_name
		self.__tag = tag
		self._command = command
		self.logger = logging.getLogger(__name__)

	def run(self) -> None:
		while self.status.current_state == NodeStatus.RUNNING:
			time.sleep(1)

	@ abstractmethod
	def _get_docker_environment(self) -> dict[str, str]:
		return {}

	def _forward_container_logs_to_python_logger(self) -> None:
		"""
		Continuously reads Docker container logs (stdout+stderr)
		and forwards them to the local Python logger.
		"""
		if not self.docker_container:
			return  # Container isn't set up
		logger = logging.getLogger(__name__)  # Or your class logger

		# logs(stream=True) yields lines as they appear
		log_stream = self.docker_container.logs(stream=True, follow=True)

		for raw_line in log_stream:
			# Decode bytes
			message = raw_line.decode('utf-8', errors='replace').rstrip()
			level = message.split(":",2)
			match level[0]:
				case "WARNING": logAtLevel = logger.warning
				case "ERROR": logAtLevel = logger.error
				case "CRITICAL": logAtLevel = logger.critical
				case "DEBUG": logAtLevel = logger.debug
				case _: logAtLevel = logger.info

			# For instance, you might want to add the container name or ID:
			logAtLevel(f"[container:{self.__container_name}] {message}")

	def deploy(self) -> None:
		try:
			self.docker_container = self.docker_client.containers.get(self.__container_name) # first check for existing containers/images

			self.docker_container.stop()
			self.docker_container.remove()

		except docker.errors.NotFound:
			pass
		try:
			self.docker_container = self.docker_client.containers.run(
				self.__image_name + f":{self.__tag}" if self.__tag else self.__image_name,
				detach=True,
				name=self.__container_name,
				network=self.docker_network_name,
				auto_remove=True,
				environment=self._get_docker_environment(),
				labels={'node': str(self.node_id)},
				command = self._command,
				volumes={"/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"}}
			)
			# Start the container
			self.docker_container.start()

			threading.Thread(
				target=self._forward_container_logs_to_python_logger,
				name=f"{self.__container_name}-log-forwarder",
				daemon=True
			).start()
		except Exception as e:
			print(f"Error deploying container on node {self.node_id}: {e}")
			raise e

	# def start_zk_client(self) -> None:
	#	 try:
	#		 self.zk = KazooClient(hosts=self.zookeeper_host)
	#		 self.zk.start()
	#	 except Exception as e:
	#		 print(
	#			 f"Error connecting to ZooKeeper from node {self.node_id}: {e}")
	#		 raise

	def shutdown(self) -> None:
		if self.status.current_state != NodeStatus.OFFLINE:
			self.status.offline()
			if self.docker_container:
				self.docker_container.stop()
				#self.docker_container.remove()
				del self.docker_container
		# TODO the following ensures that the container is removed, even if we somehow lost connection to it. Is this needed?
		try:
			existing_container = self.docker_client.containers.get(
				self.__container_name)
			existing_container.stop()
			#existing_container.remove()
		except docker.errors.NotFound:
			pass  # No existing container, proceed

	def _report_status(self) -> dict[str, Any]:
		if hasattr(self, 'docker_container'):
			assert self.docker_container
			name = self.docker_container.name
		else:
			name = "None"
		# TODO Optionally, we can add more detailed status information
		return {
			'container': name
		}

	def collect_machine_info(self) -> Machine:
		return self.machine_info

	def receive_message(self, message: str) -> None:
		raise NotImplementedError()

	@staticmethod
	def create_runtime_environment(
		role: str,
		machine: Machine,
		zookeeper_host: str = "zookeeper",
		hdfs_host: str = "hdfs2name") -> dict[str, str]:
		"""
		Returns environment variables for either a Task Manager or a Workflow Manager,
		depending on `role` ('task_manager' or 'workflow_manager').
		"""
		# Common to both roles:
		env = {
			"ROLE": role,
			"ZOOKEEPER_HOST": zookeeper_host,
			"NODE_ID": str(machine.ID),
			"HDFS_NAMENODE": f"hdfs://{hdfs_host}:8020",
			"METAPHACTORY_INTERNAL":"http://172.22.0.1:10214", # TODO set this address dynamically when containert starts
			"METAPHACTORY_EXTERNAL":"http://localhost:10214"
		}

		# If you need separate fields for Task vs. Workflow,
		# handle them conditionally:
		if role == "task_manager":
			env["TM_ADDR"] = machine.descriptor.address
			env["TM_HOSTNAME"] = machine.descriptor.host_name
			env["TM_CPU_CORES"] = str(machine.descriptor.cpu_cores)
			env["TM_RAM_SIZE"] = str(machine.descriptor.ram_size)
			env["TM_HDD_SIZE"] = str(machine.descriptor.hdd)
		elif role == "workflow_manager":
			env["WM_ADDR"] = machine.descriptor.address
			env["WM_HOSTNAME"] = machine.descriptor.host_name
			env["WM_CPU_CORES"] = str(machine.descriptor.cpu_cores)
			env["WM_RAM_SIZE"] = str(machine.descriptor.ram_size)
			env["WM_HDD_SIZE"] = str(machine.descriptor.hdd)
		elif role == "dashboard":
			env["DASHBOARD_ADDR"] = machine.descriptor.address
			env["DASHBOARD_HOSTNAME"] = machine.descriptor.host_name
			env["DASHBOARD_CPU_CORES"] = str(machine.descriptor.cpu_cores)
			env["DASHBOARD_RAM_SIZE"] = str(machine.descriptor.ram_size)
			env["DASHBOARD_HDD_SIZE"] = str(machine.descriptor.hdd)

		return env

# ----------------------------------------
# ZOOKEEPER NODE
# ----------------------------------------
class ZookeeperNode(SimulatedNode):

	def __init__(self, machine: Machine, docker_network_name: str) -> None:

		self.__container_name = "zookeeper"
		self.__image_name = "zookeeper"
		self.__tag = "3.7"  # Or whatever version you prefer
		self.__host_port = 2181
		super().__init__(machine,
						 docker_network_name,
						 self.__container_name,
						 self.__image_name, self.__tag,
						 {'2181/tcp': self.__host_port}
						 )

		self.__zookeeper_environment = {
			'ZOOKEEPER_CLIENT_PORT': '2181',
			'ZOOKEEPER_TICK_TIME': '2000',
			'ZOOKEEPER_INIT_LIMIT': '5',
			'ZOOKEEPER_SYNC_LIMIT': '2',
			'ZOO_4LW_COMMANDS_WHITELIST': '*',
			'KAFKA_OPTS': "-Dzookeeper.4lw.commands.whitelist=*"
		}

		self.zookeeper_host = 'localhost:' + str(self.__host_port)

		try:
			self.docker_client.images.pull(self.__image_name, tag=self.__tag)
		except Exception as e:
			raise e
		self.status.ready()

	def _get_docker_environment(self) -> dict[str, str]:
		return self.__zookeeper_environment

	def _is_zk_running(self) -> bool:
		command = f'sh -c "echo ruok | nc {self.__container_name} 2181"'
		try:
			output = self.docker_client.containers.run(
				self.__container_name,
				command=command,
				network=self.docker_network_name,
				remove=True
			)
			if b'imok' in output:
				return True
			else:
				return False
		except Exception as e:
			raise e

	def wait_for_zookeeper(self, timeout: int) -> None:
		"""Wait at most timeout seconds for zookeeper to come online"""

		polling_shortest_s = 0.010
		current_waiting_time = polling_shortest_s
		total_waiting_time = 0
		while True:
			try:
				if self._is_zk_running():
					return
			except Exception as e:
				logging.getLogger(__name__).debug(
					"Got an exception while checking zookeeper availability, this happens usually when the zookeeper is not yet running. " + str(e))
			logging.getLogger(__name__).info(
				f"Zookeeper not yet available. Waiting {current_waiting_time} seconds for it to become available")
			time.sleep(current_waiting_time)
			total_waiting_time += current_waiting_time
			if math.isclose(total_waiting_time, timeout):
				raise Exception(
					f"Zookeeper is not available after trying for {timeout} seconds.")

			current_waiting_time = current_waiting_time * 2

			if total_waiting_time + current_waiting_time > timeout:
				current_waiting_time = timeout - total_waiting_time

# ----------------------------------------
# HDFS NODE
# ----------------------------------------
class HDFSDataNode(SimulatedNode):
	def __init__(self, machine: Machine, docker_network_name: str) -> None:
		self.__container_name = f"hdfs{machine.ID}data"
		self.__image_name = "gradiant/hdfs-datanode"
		self.__tag = None#"3.2.1" # or a pinned version

		super().__init__(
			machine,
			docker_network_name,
			container_name=self.__container_name,
			image_name=self.__image_name,
			tag=None,
			ports={
				# If you want to expose HDFS outside Docker, you can map:
				# '8020/tcp': 8020,  # RPC
				# '9870/tcp': 9870,  # NameNode web UI
				# etc.
			},
			command=f"/run.sh"
		)
		self.status.ready()

		# For single-node usage, bitnami/hadoop typically needs:
		self.__hdfs_environment = {
			# "HADOOP_MODE": "single",
			# "HADOOP_DAEMON_TYPE": "namenode",
			# "ALLOW_PSEUDODISTRIBUTED": "yes",
			"CORE_CONF_fs_defaultFS":f"hdfs://hdfs{machine.ID}name:8020",
			"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/jvm/java-1.8-openjdk/jre/bin:/usr/lib/jvm/java-1.8-openjdk/bin:/opt/hadoop/bin"
		}

	def _get_docker_environment(self) -> dict[str, str]:
		return self.__hdfs_environment

class HDFSNode(SimulatedNode):
	def __init__(self, machine: Machine, docker_network_name: str) -> None:
		self.__container_name = f"hdfs{machine.ID}name"
		self.__image_name = "gradiant/hdfs-namenode"
		self.__tag = None#"3.2.1" # or a pinned version

		super().__init__(
			machine,
			docker_network_name,
			container_name=self.__container_name,
			image_name=self.__image_name,
			tag=None,
			ports={
				# If you want to expose HDFS outside Docker, you can map:
				# '8020/tcp': 8020,  # RPC
				# '9870/tcp': 9870,  # NameNode web UI
				# etc.
			},
			command=f"/run.sh"
		)
		self.status.ready()

		# For single-node usage, bitnami/hadoop typically needs:
		self.__hdfs_environment = {
			# "HADOOP_MODE": "single",
			# "HADOOP_DAEMON_TYPE": "namenode",
			# "ALLOW_PSEUDODISTRIBUTED": "yes",
			# optionally define more variables,
			"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/jvm/java-1.8-openjdk/jre/bin:/usr/lib/jvm/java-1.8-openjdk/bin:/opt/hadoop/bin"
		}

	def _get_docker_environment(self) -> dict[str, str]:
		return self.__hdfs_environment

	def create_hdfs_directory(self, directory: str) -> None:
		"""
		Creates the given directory in HDFS within this container,
		ignoring if it already exists.
		"""
		logger = logging.getLogger(__name__)

		mkdir_cmd = f"hdfs dfs -mkdir {directory}"
		chmod_cmd = f"hdfs dfs -chmod 777 {directory}"

		#logger.info(f"{directory} {mkdir_cmd} {chmod_cmd}")

		# 1) Make the directory (with -p so it won’t fail if it already exists)
		result = self.docker_container.exec_run(mkdir_cmd)
		if result.exit_code != 0:
			logger.warning(f"Could not create directory {directory}: {result.output}")

		# 2) Adjust permissions (optional, if you want to be sure it’s writable)
		result = self.docker_container.exec_run(chmod_cmd)
		if result.exit_code != 0:
			logger.warning(f"Could not chmod 777 on {directory}: {result.output}")

	def wait_for_hdfs(self, timeout: int = 200) -> None:
		"""
		Wait up to 'timeout' seconds for HDFS to become ready by:
		- Successfully running 'hdfs dfs -ls /' (showing NameNode is up).
		- Confirming 'hdfs dfsadmin -safemode get' shows "Safe mode is OFF".
		"""
		logger = logging.getLogger(__name__)

		polling_interval = 6
		total_wait = 0


		if not self.docker_container:
			raise RuntimeError("docker_container not set; cannot run HDFS checks.")

		while total_wait < timeout:
			try:
				# 1) Check if 'hdfs dfs -ls /' succeeds
				exec_result = self.docker_container.exec_run("hdfs dfs -mkdir /tmp")
				exec_result = self.docker_container.exec_run("hdfs dfs -ls /")
				output_bytes = exec_result.output

				if exec_result.exit_code == 0:
					# Look for typical strings that show the NameNode responded
					if (b"Found" in output_bytes or
						b"No such file" in output_bytes or
						b"drwx" in output_bytes):
						logger.info("HDFS is up and responding to 'hdfs dfs -ls /'")

						self.docker_container.exec_run("hdfs dfsadmin -safemode leave")

						# 2) Now also ensure safe mode is OFF
						# Pseudocode from earlier:
						while True:
							safe_mode_result = self.docker_container.exec_run("hdfs dfsadmin -safemode get")
							if b"Safe mode is OFF" in safe_mode_result.output:
								logger.info("Safe mode is OFF, HDFS is fully ready for writes!")
								return
							else:
								logger.info("NameNode still in safe mode; sleeping 2s")
								time.sleep(2)
								total_wait += 2

							if total_wait >= timeout:
								raise TimeoutError(f"HDFS is stuck in safe mode after {timeout} seconds.")
					# If we didn't return inside the safe-mode check above,
					# we'll reach here and keep polling again.
				else:
					logger.debug(f"'hdfs dfs -ls /' exit_code={exec_result.exit_code}, output={output_bytes!r}")

			except Exception as ex:
				logger.debug(f"HDFS not ready yet: {ex}")

			logger.info(f"HDFS not up (or still in safe mode); sleeping {polling_interval}s")
			time.sleep(polling_interval)
			total_wait += polling_interval

		raise TimeoutError(f"HDFS still not ready after {timeout} seconds.")

# ----------------------------------------
# WORKFLOW MANAGER NODE
# ----------------------------------------
class WorkflowManagerNode(SimulatedNode):

	def __init__(self, machine: Machine, docker_network_name: str) -> None:
		self.__container_name = f"workflow_manager_{machine.ID}"
		print(__name__ + ": CURRENTLY USING ALPINE IMAGE FOR WFM")
		self.__image_name = "gm/runtime"
		self.__tag = "latest"  # Or whatever version you prefer

		super().__init__(machine,
						 docker_network_name,
						 self.__container_name,
						 self.__image_name,
						 self.__tag,
						 {}
						 )

		# Use the static helper function
		self.__workflow_manager_environment = SimulatedNode.create_runtime_environment(
			role="workflow_manager",
			machine = machine,
			zookeeper_host="zookeeper"
		)
		self.status.ready()

	def _get_docker_environment(self) -> dict[str, str]:
		return self.__workflow_manager_environment

# ----------------------------------------
# TASK MANAGER NODE
# ----------------------------------------
class TaskManagerNode(SimulatedNode):
	def __init__(self, machine: Machine, docker_network_name: str) -> None:
		self.__container_name = f"task_manager_{machine.ID}"
		print(__name__ + ": CURRENTLY USING ALPINE IMAGE FOR TM")
		self.__image_name = "gm/runtime"
		self.__tag = "latest"  # Or whatever version you prefer

		super().__init__(machine,
						 docker_network_name,
						 self.__container_name,
						 self.__image_name,
						 self.__tag,
						 {}
						 )

		self.__task_manager_environment = SimulatedNode.create_runtime_environment(
			role="task_manager",
			machine=machine,
			zookeeper_host="zookeeper"
		)
		self.status.ready()

	def run(self,alg,args): # TEMP RUN FOR VALIDATING WHILE FINISHING EXECUTION CONTROLLER AND DATA MANAGER
		self.logger.info(f"Pretending to run {alg} in {self}")
		out = alg(args)
		self.logger.info(f"Pretend result: {out}")

	def _get_docker_environment(self) -> dict[str, str]:
		return self.__task_manager_environment

# ----------------------------------------
# DASHBOARD NODE
# ----------------------------------------
class DashboardNode(SimulatedNode):

	def __init__(self, machine: Machine, docker_network_name: str) -> None:
		self.__container_name = f"dashboard_{machine.ID}"
		print(__name__ + ": CURRENTLY USING ALPINE IMAGE FOR DASHBOARD")
		self.__image_name = "gm/runtime"
		self.__tag = "latest"  # Or whatever version you prefer

		super().__init__(machine,
						 docker_network_name,
						 self.__container_name,
						 self.__image_name,
						 self.__tag,
						 {}
						 )

		# Use the static helper function
		self.__dashboard_environment = SimulatedNode.create_runtime_environment(
			role="dashboard",
			machine = machine,
			zookeeper_host="zookeeper"
		)
		self.status.ready()

	def _get_docker_environment(self) -> dict[str, str]:
		return self.__dashboard_environment
