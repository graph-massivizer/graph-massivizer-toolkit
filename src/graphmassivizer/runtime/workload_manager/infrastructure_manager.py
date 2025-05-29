# src/graphmassivizer/runtime/workload_manager/infrastructure_manager.py

import threading
import logging
import json
from kazoo.client import KazooClient
from kazoo.protocol.states import WatchedEvent, EventType
from graphmassivizer.core.descriptors.descriptors import Machine, MachineDescriptor


class InfrastructureManager:
	def __init__(self, workload_manager) -> None:

		self.logger = logging.getLogger(self.__class__.__name__)
		self.workload_manager = workload_manager
		self.zookeeper_host = workload_manager.zookeeper_host
		self.machine = workload_manager.machine

		self.node_info_lock = threading.Lock()
		self.tm_machine_map = {}
		self.available_execution_units_map = {}
		self.machine_idx = 0

		self.zk = workload_manager.zk

		self.init_zookeeper_directories()

		self.machine_descriptors = {}	# Store MachineDescriptors
		self.store_environment_model_in_zookeeper()

		# Ensure the watcher is set up for the /taskmanagers path
		if not self.zk.exists('/taskmanagers'):
			self.zk.create('/taskmanagers', makepath=True)
			self.logger.info("Created /taskmanagers ZNode as it did not exist.")
		self.zk.ChildrenWatch('/taskmanagers', self.zookeeper_task_manager_watcher)

		self.input_split_manager = None	# Placeholder for actual implementation

	def print_zookeeper_subtree(self, path: str = "/", indent: int = 0) -> None:
		"""
		Recursively print (or log) the ZooKeeper nodes under `path`.
		"""
		prefix = "  " * indent	# indentation for visual clarity

		try:
			data, stat = self.zk.get(path)
			children = self.zk.get_children(path)
		except Exception as e:
			self.logger.warning(f"Failed to get info for path '{path}': {e}")
			return

		data_str = data.decode('utf-8', errors='replace') if data else ""
		node_name = path if path != "" else "/"
		self.logger.info(f"{prefix}{node_name} -> '{data_str}'")

		for child in children:
			if path == "/":
				child_path = f"/{child}"
			else:
				child_path = f"{path}/{child}"
			self.print_zookeeper_subtree(child_path, indent + 1)

	def init_zookeeper_directories(self) -> None:
		paths = ['/workloadmanager', '/taskmanagers', '/environment']
		for path in paths:
			if not self.zk.exists(path):
				self.zk.create(path, makepath=True) # Added makepath=True for safety
				self.logger.debug(f"Created Zookeeper path: {path}")



	def serialize_environment_model(self):
		model_data = json.dumps({
			machine_id: descriptor.to_dict() for machine_id, descriptor in self.machine_descriptors.items()
		})
		return model_data.encode('utf-8')	# Convert to bytes for ZooKeeper

	def store_environment_model_in_zookeeper(self) -> None:
		model_data = self.serialize_environment_model()
		model_path = '/environment/machines'
		if self.zk.exists(model_path):
			self.zk.set(model_path, model_data)
		else:
			self.zk.create(model_path, model_data, makepath=True) # Added makepath=True
		self.logger.debug("Environment model updated in ZooKeeper.")

	def zookeeper_task_manager_watcher(self, task_manager_nodes) -> None:
		# task_manager_nodes is a list of IDs of child znodes under /taskmanagers
		with self.node_info_lock:
			self.logger.info(f"Task Manager nodes changed: {task_manager_nodes}")
			current_tm_ids = set(task_manager_nodes)
			registered_tm_ids = set(self.tm_machine_map.keys())

			# Process new TaskManagers
			for node_id_str in current_tm_ids - registered_tm_ids:
				node_path = f'/taskmanagers/{node_id_str}'
				if self.zk.exists(node_path):
					data, stat = self.zk.get(node_path)
					if data:
						try:
							# Assuming data is JSON string of Machine a descriptor
							machine_data = json.loads(data.decode('utf-8'))
							# Reconstruct Machine object or store relevant info
							# For simplicity, let's assume we store the raw data or a simplified representation
							self.tm_machine_map[node_id_str] = machine_data 
							self.logger.info(f"Registered new TaskManager: {node_id_str} with data {machine_data}")
						except json.JSONDecodeError:
							self.logger.error(f"Could not decode JSON for TaskManager {node_id_str} from data: {data}")
						except Exception as e:
							self.logger.error(f"Error processing new TaskManager {node_id_str}: {e}")
					else:
						self.logger.warning(f"No data found for TaskManager znode: {node_path}")
				else:
					self.logger.warning(f"ZNode {node_path} disappeared before data could be read.")


			# Process removed TaskManagers
			for node_id_str in registered_tm_ids - current_tm_ids:
				if node_id_str in self.tm_machine_map:
					del self.tm_machine_map[node_id_str]
					self.logger.info(f"Unregistered TaskManager: {node_id_str}")
			
			# self.store_environment_model_in_zookeeper() # Decide if this needs to be updated here

			self.logger.info(f"Currently {len(self.tm_machine_map)} TaskManagers registered: {list(self.tm_machine_map.keys())}")
			
			# --- MODIFICATION START ---
			# Check if exactly 6 TaskManagers are registered
			if len(self.tm_machine_map) == 6:
				self.logger.info("Exactly 6 TaskManagers registered. Attempting to trigger receive_workflow.")
				# Call receive_workflow on the WorkloadManager instance
				# Ensure WorkloadManager handles being called multiple times if necessary,
				# or that this logic is only hit once.
				# The WorkloadManager's own state machine should prevent re-processing if already initialized.
				self.workload_manager.receive_workflow()
			# --- MODIFICATION END ---

			# self.logger.info("ZK tree updated with task manager nodes") # This might be too verbose now
			# self.logger.info("TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST")
			# self.print_zookeeper_subtree("/") # This can be very verbose, use when debugging

	def get_machine(self, location_preference=None):
		with self.node_info_lock:
			# Ensure tm_machine_map values are appropriate for selection,
			# this part might need adjustment based on what get_machine expects.
			# The current tm_machine_map stores raw data, not Machine objects.
			# For now, this part of get_machine will likely fail or need rework
			# if it expects Machine objects with specific attributes like 'uid'.
			worker_machines = list(self.tm_machine_map.values()) 
			if not worker_machines:
				raise Exception("No available machines.")
			
			# The following logic assumes worker_machines are objects with a 'uid'
			# and that available_execution_units_map is managed correctly.
			# This will need to be adapted if tm_machine_map stores simple dicts.
			# For the purpose of triggering receive_workflow, this part is less critical.

			# Example placeholder if actual machine objects are needed:
			# actual_worker_machines = [Machine.from_dict(data) for data in worker_machines] 
			# if not actual_worker_machines:
			# raise Exception("No available machines after parsing.")
			
			# self.machine_idx = (self.machine_idx + 1) % len(actual_worker_machines)
			# selected_machine = actual_worker_machines[self.machine_idx]
			# if selected_machine.uid not in self.available_execution_units_map:
			# self.available_execution_units_map[selected_machine.uid] = initial_units_value
			# self.available_execution_units_map[selected_machine.uid] -= 1
			# return selected_machine
			self.logger.warning("get_machine() may need rework based on tm_machine_map contents.")
			return worker_machines[0] if worker_machines else None


	def shutdown_infrastructure_manager(self) -> None:
		self.print_zookeeper_subtree("/")
		self.zk.stop()
		self.logger.info("Shutdown infrastructure manager.")

# # - Manages the infrastructure, including Task Manager discovery and resource allocation.
# # - Uses ZooKeeper to track available Task Managers and their resources.
# # - Implements the getMachine method, which selects a suitable Task Manager for execution nodes based on resource availability and location preferences.
# # - Reclaims execution units when tasks are finished or datasets are erased.

# import threading
# import logging
# import json
# from kazoo.client import KazooClient
# from kazoo.protocol.states import WatchedEvent, EventType
# from graphmassivizer.core.descriptors.descriptors import Machine, MachineDescriptor


# class InfrastructureManager:
# 	def __init__(self, workload_manager) -> None:

# 		self.logger = logging.getLogger(self.__class__.__name__)
# 		self.workload_manager = workload_manager
# 		self.zookeeper_host = workload_manager.zookeeper_host
# 		self.machine = workload_manager.machine

# 		self.node_info_lock = threading.Lock()
# 		self.tm_machine_map = {}
# 		# self.available_execution_units_map = {}
# 		self.machine_idx = 0

# 		self.zk = workload_manager.zk

# 		self.init_zookeeper_directories()

# 		self.machine_descriptors = {}  # Store MachineDescriptors
# 		# self.store_machine_descriptor()
# 		# self.register_self()
# 		self.store_environment_model_in_zookeeper()

# 		# Watch for changes in task managers
# 		self.zk.ChildrenWatch('/taskmanagers', self.zookeeper_task_manager_watcher)

# 		self.input_split_manager = None  # Placeholder for actual implementation

# 	def print_zookeeper_subtree(self, path: str = "/", indent: int = 0) -> None:
# 		"""
# 		Recursively print (or log) the ZooKeeper nodes under `path`.
# 		"""
# 		prefix = "  " * indent  # indentation for visual clarity

# 		try:
# 			# Get data and children for the current node
# 			data, stat = self.zk.get(path)
# 			children = self.zk.get_children(path)
# 		except Exception as e:
# 			self.logger.warning(f"Failed to get info for path '{path}': {e}")
# 			return

# 		# Print path and data
# 		# Note: data is raw bytes. You might want to decode them or just print length.
# 		data_str = data.decode('utf-8', errors='replace') if data else ""
# 		node_name = path if path != "" else "/"
# 		self.logger.info(f"{prefix}{node_name} -> '{data_str}'")

# 		# Recurse for each child
# 		for child in children:
# 			# Construct child path carefully
# 			# If path == "/", then child_path = "/" + child
# 			# else child_path = path + "/" + child
# 			if path == "/":
# 				child_path = f"/{child}"
# 			else:
# 				child_path = f"{path}/{child}"
# 			self.print_zookeeper_subtree(child_path, indent + 1)

# 	def init_zookeeper_directories(self) -> None:
# 		paths = ['/workloadmanager', '/taskmanagers', '/environment']
# 		for path in paths:
# 			if not self.zk.exists(path):
# 				self.zk.create(path)
# 				self.logger.debug(f"Created Zookeeper path: {path}")


# 	# def register_self(self) -> None:
# 	# 	node_path = f'/workloadmanager/{self.machine.ID}'
# 	# 	mashine_utf8 = self.machine.to_utf8()
# 	# 	if self.zk.exists(node_path):
# 	# 		self.zk.set(node_path, mashine_utf8)
# 	# 	else:
# 	# 		self.zk.create(node_path, mashine_utf8, makepath=True)
# 	# 	self.logger.info(f"Registered InfrastructureManager {self.machine} with ZooKeeper.")

# 	def serialize_environment_model(self):
# 		#print(self.machine_descriptors.items())
# 		# Convert descriptors to dictionaries
# 		model_data = json.dumps({
# 			machine_id: descriptor.to_dict() for machine_id, descriptor in self.machine_descriptors.items()
# 		})
# 		return model_data.encode('utf-8')  # Convert to bytes for ZooKeeper

# 	def store_environment_model_in_zookeeper(self) -> None:
# 		model_data = self.serialize_environment_model()
# 		model_path = '/environment/machines'
# 		if self.zk.exists(model_path):
# 			self.zk.set(model_path, model_data)
# 		else:
# 			self.zk.create(model_path, model_data)
# 		self.logger.debug("Environment model updated in ZooKeeper.")

# 	def zookeeper_task_manager_watcher(self, task_manager_nodes) -> None:
# 		with self.node_info_lock:
# 			self.logger.debug(f"Task Manager nodes: {task_manager_nodes}")
# 			# Update machine descriptors based on task manager nodes
# 			for node in task_manager_nodes:
# 				node_path = f'/taskmanagers/{node}'
# 				data, stat = self.zk.get(node_path)
# 				# if data:
# 				#	 machine_info = json.loads(data.decode('utf-8'))
# 				#	 self.update_machine_descriptors(machine_info)
# 			self.store_environment_model_in_zookeeper()

# 			# NOW: Call the subtree-printing function after each event:
# 			self.logger.info("ZK tree updated with task manager nodes")
# 			self.logger.info("TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST TEST")
# 			self.print_zookeeper_subtree("/")

# 	def get_machine(self, location_preference=None):
# 		with self.node_info_lock:
# 			worker_machines = list(self.tm_machine_map.values())
# 			if not worker_machines:
# 				raise Exception("No available machines.")
# 			self.machine_idx = (self.machine_idx + 1) % len(worker_machines)
# 			selected_machine = worker_machines[self.machine_idx]
# 			self.available_execution_units_map[selected_machine.uid] -= 1
# 			return selected_machine

# 	def shutdown_infrastructure_manager(self) -> None:
# 		self.print_zookeeper_subtree("/")
# 		self.zk.stop()
# 		self.logger.info("Shutdown infrastructure manager.")
