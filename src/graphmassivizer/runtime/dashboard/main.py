# - The main class responsible for workload management.
# - Implements IClientWMProtocol and ITM2WMProtocol to handle communication with clients and Task Managers.
# - Manages sessions and topologies submitted by clients.
# - Provides functionalities for dataset management (gather, scatter, erase, assign).
# - Monitors cluster utilization and resource usage.

import os
import json
import ast
import logging
import logging.handlers
from kazoo.client import KazooClient
from dash import Dash
from layout import get_layout
from callbacks import register_callbacks
import config
import docker
import time
import concurrent.futures
import stat
import sys
import pandas as pd
import threading
import dash_bootstrap_components as dbc
from datetime import datetime, timezone
from data_loader import workflow_DAG_to_graph_elements
from graphmassivizer.runtime.workload_manager.infrastructure_manager import InfrastructureManager
from graphmassivizer.core.descriptors.descriptors import Machine
from graphmassivizer.core.zookeeper.zookeeper_state_manager import ZookeeperStateManager

class Dashboard:

	def __init__(self, zookeeper_host, docker_network_name) -> None:
		self.logger = logging.getLogger(self.__class__.__name__)
		self.zookeeper_host = zookeeper_host
		self.zk = ZookeeperStateManager(hosts=self.zookeeper_host)
		self.machine = Machine.parse_from_env(self.zk,prefix="DASHBOARD_")
		self.register_self()
		self.docker_network_name = docker_network_name
		self.client_docker = docker.DockerClient(base_url='unix:///var/run/docker.sock')#docker.from_env()#

	def register_self(self) -> None:
		node_path = f'/dashboard/{self.machine.ID}'
		mashine_utf8 = self.machine.to_utf8()
		if self.zk.exists(node_path):
			self.zk.set(node_path, mashine_utf8)
		else:
			self.zk.create(node_path, mashine_utf8, makepath=True)
		self.logger.info(f"Registered Dashboard {self.machine} with ZooKeeper.")

	# getting nodes connected to zookeeper node

	def check_docker_socket(self):
		"""Check if Docker socket exists and is accessible"""
		socket_path = "/var/run/docker.sock"
		try:
			os.chmod(socket_path, stat.S_IRWXG)  # Grant full access (use cautiously)
			print("Permissions updated successfully!")
		except PermissionError:
			print("Permission denied ❌ - Try running as root.")

		if not os.access(socket_path, os.R_OK | os.W_OK):
			raise PermissionError(f"No read/write access to {socket_path}. Try running as root or fixing permissions.")
		if not os.path.exists(socket_path):
			raise FileNotFoundError(f"Docker socket not found at {socket_path}")

	def list_containers_info_in_network(self):
		"""List all containers info in a specific Docker network"""
		try:
			# Ensure Docker socket is accessible
			self.check_docker_socket()

			# Connect to Docker API
			#self.client_docker = docker.from_env()#docker.DockerClient(base_url="unix://var/run/docker.sock")

			# Get network details
			network = self.client_docker.networks.get(self.docker_network_name)

			# List connected containers
			containers = network.containers

			print(f"Containers info in network '{self.docker_network_name}':")
			containers_info = {"Container Name": [], "Status": [], "Host Name":[]}#, "CPU Percent":[], "Memory Usage":[]}
			for container in containers:
				'''
				# capturing cpu & mem usage of containers
				# todo
				stats = container.stats(stream=False)

				# CPU Usage calculation
				cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
				system_cpu_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
				cpu_percent = (cpu_delta / system_cpu_delta * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"])) * 100.0 if system_cpu_delta > 0 else 0.0

				# Memory Usage
				mem_usage = stats["memory_stats"]["usage"]
				mem_limit = stats["memory_stats"]["limit"]
				mem_percent = (mem_usage / mem_limit) * 100.0 if mem_limit > 0 else 0.0
				'''

				container_attrs = container.attrs

				# Get the host machine name (if available)
				container_host_name = container_attrs.get("Config", {}).get("Hostname", "Unknown")
				#_, output = container.exec_run("ip route | awk '/default/ { print $3 }'")
				#host_ip = output.decode().strip()
				#print(f"Host machine IP: {host_ip}")
				#containers_info[container.name] = [container.status, container_host_name]
				containers_info["Container Name"].append(container.name)
				containers_info["Status"].append(container.status)
				containers_info["Host Name"].append(container_host_name)
				#containers_info["CPU Percent"].append(cpu_percent)
				#containers_info["Memory Usage"].append(mem_percent)

			containers_info_df = pd.DataFrame(data=containers_info)

			return containers_info_df

		except FileNotFoundError as e:
			self.logger.error(f"Error: {e}")
		except PermissionError as e:
			self.logger.error(f"Error: {e}")
			self.logger.error("Try running the container with the correct permissions.")
		except docker.errors.APIError as e:
			self.logger.error(f"Docker API error: {e}")
		except Exception as e:
			self.logger.error(f"Unexpected error: {e}")

	def list_all_containers_info_in_network(self):
		"""List all containers info in a specific Docker network including stopped ones"""
		try:
			self.check_docker_socket()
			#self.client_docker = docker.DockerClient(base_url="unix://var/run/docker.sock")
			network_name = self.docker_network_name
			all_containers = self.client_docker.containers.list(all=True)

			containers_info = {
				"Container Name": [],
				"Status": [],
				"Host Name": [],
				"CPU Usage Percent": [],
				"Memory Usage Percent": []
			}

			for container in all_containers:
				networks = container.attrs['NetworkSettings']['Networks']
				if network_name in networks:
					container_host_name = container.attrs.get("Config", {}).get("Hostname", "Unknown")

					containers_info["Container Name"].append(container.name)
					containers_info["Status"].append(container.status)
					containers_info["Host Name"].append(container_host_name)

					# Fetch CPU & Memory stats with timeout
					stats = self.fetch_container_stats_with_timeout(container, timeout=3)

					if stats:
						containers_info["CPU Usage Percent"].append(stats["cpu_percent"])
						containers_info["Memory Usage Percent"].append(stats["mem_percent"])
					else:
						containers_info["CPU Usage Percent"].append(None)
						containers_info["Memory Usage Percent"].append(None)

			containers_info_df = pd.DataFrame(data=containers_info)
			return containers_info_df

		except Exception as e:
			print(f"Unexpected error: {e}")
			return None

	def list_all_containers_info_in_network_multithread(self):
		"""List all containers info in a specific Docker network using multithreading"""
		try:
			self.check_docker_socket()
			#self.client_docker = docker.DockerClient(base_url="unix://var/run/docker.sock")
			network_name = self.docker_network_name

			all_containers = self.client_docker.containers.list(all=True)
			containers_info = {"Container Name": [], "Status": [], "Host Name": [], "CPU Usage Percent": [], "Memory Usage Percent": [], 'Memory Usage (Bytes)': [], 'Age (Minutes)':[]}

			# Identify containers in the target network
			target_containers = []
			for container in all_containers:
				networks = container.attrs['NetworkSettings']['Networks']
				if network_name in networks:
					target_containers.append(container)

			# Fetch stats concurrently using ThreadPoolExecutor
			with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
				future_to_container = {executor.submit(self.fetch_container_stats, container): container for container in target_containers}

				for future in concurrent.futures.as_completed(future_to_container):
					stats = future.result()
					#print(f'container stats {stats}')
					container = future_to_container[future]

					# Store the data in the dictionary
					containers_info["Container Name"].append(container.name)
					containers_info["Status"].append(container.status)
					containers_info["Host Name"].append(container.attrs.get("Config", {}).get("Hostname", "Unknown"))
					containers_info["CPU Usage Percent"].append(stats["cpu_percent"])
					containers_info["Memory Usage Percent"].append(stats["mem_percent"])
					containers_info["Memory Usage (Bytes)"].append(stats['mem_usage'])
					# Get container age
					# Get the creation time of the container
					created_at = container.attrs.get("Created", None)
					#print(f'container created at {created_at}')
					if not created_at is None:
						created_at = created_at[:26]
						# Convert the string timestamp to a datetime object
						created_at_dt = datetime.strptime(created_at[:-1], "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone.utc)
						# Get the current time in UTC
						now = datetime.now(timezone.utc)
						# Calculate the age of the container (in minutes)
						container_age = round((now - created_at_dt).total_seconds() / 60, 2)
					else:
						container_age = None

					#print(f'container age {container_age}')
					containers_info['Age (Minutes)'].append(container_age)


			containers_info_df = pd.DataFrame(data=containers_info)

			return containers_info_df  # Use this to update your dashboard

		except Exception as e:
			print(f"❌ Unexpected error: {e}")
			return None

	def fetch_container_stats(self, container):
		"""Fetch container CPU & Memory stats"""
		try:
			stats = container.stats(stream=False)

			cpu_stats = stats.get("cpu_stats", {})
			precpu_stats = stats.get("precpu_stats", {})

			total_usage = cpu_stats.get("cpu_usage", {}).get("total_usage")
			pre_total_usage = precpu_stats.get("cpu_usage", {}).get("total_usage")
			system_cpu_usage = cpu_stats.get("system_cpu_usage")
			pre_system_cpu_usage = precpu_stats.get("system_cpu_usage")

			if None in (total_usage, pre_total_usage, system_cpu_usage, pre_system_cpu_usage):
				cpu_percent = 0.0
			else:
				cpu_delta = total_usage - pre_total_usage
				system_cpu_delta = system_cpu_usage - pre_system_cpu_usage
				num_cpus = len(cpu_stats.get('cpu_usage', {}).get('percpu_usage', [])) or 1 # tocheck
				cpu_percent = (cpu_delta / system_cpu_delta * num_cpus) * 100.0 if system_cpu_delta > 0 else 0.0
				cpu_percent = round(cpu_percent, 2)

			memory_stats = stats.get("memory_stats", {})
			mem_usage = memory_stats.get("usage")
			mem_limit = memory_stats.get("limit")

			if None in (mem_usage, mem_limit) or mem_limit == 0:
				mem_percent = 0.0
			else:
				mem_percent = (mem_usage / mem_limit) * 100.0
				mem_percent = round(mem_percent, 2)

			return {"cpu_percent": cpu_percent, "mem_percent": mem_percent, "container_name": container.name, 'mem_usage': mem_usage}

		except Exception as e:
			print(f"❌ Error retrieving stats for {container.name}: {e}")
			return {"cpu_percent": None, "mem_percent": None, "container_name": container.name, 'mem_usage': None}

	# temp maybe merge with fetch_container_stats()
	# tocheck
	def get_containers_cpu_usage(self):
		"""Fetch total CPU usage for all running containers."""
		self.check_docker_socket()
		#self.client_docker = docker.DockerClient(base_url="unix://var/run/docker.sock")
		network_name = self.docker_network_name

		all_containers = self.client_docker.containers.list(all=True)

		# Identify containers in the target network
		target_containers = []
		for container in all_containers:
			networks = container.attrs['NetworkSettings']['Networks']
			if network_name in networks:
				target_containers.append(container)

		# for now I consider all containers on one machine (all_containers), later we will have cpu usage sum over host machines
		if not 'all_containers' in config.cpu_usages:
			config.cpu_usages['all_containers'] = []

		total_cpu_usage = 0.0
		for container in target_containers:
			container_name = container.name
			try:
				stats = container.stats(stream=False)
				cpu_stats = stats.get("cpu_stats", {})
				precpu_stats = stats.get("precpu_stats", {})

				total_usage = cpu_stats.get("cpu_usage", {}).get("total_usage")
				pre_total_usage = precpu_stats.get("cpu_usage", {}).get("total_usage")
				system_cpu_usage = cpu_stats.get("system_cpu_usage")
				pre_system_cpu_usage = precpu_stats.get("system_cpu_usage")

				if None in (total_usage, pre_total_usage, system_cpu_usage, pre_system_cpu_usage):
					continue  # Skip containers with missing data

				# Calculate CPU usage percentage for each container
				cpu_delta = total_usage - pre_total_usage
				system_cpu_delta = system_cpu_usage - pre_system_cpu_usage
				# tocheck
				num_cpus = len(cpu_stats.get('cpu_usage', {}).get('percpu_usage', [])) or 1
				cpu_percent = (cpu_delta / system_cpu_delta) * 100.0 if system_cpu_delta > 0 else 0.0

				# save per container cpu  history
				if not container_name in config.cpu_usages:
					config.cpu_usages[container_name] = []
				config.cpu_usages[container_name].append(cpu_percent)

				total_cpu_usage += cpu_percent

			except Exception as e:
				print(f"Error fetching stats for container {container.name}: {e}")

		config.cpu_usages['all_containers'].append(total_cpu_usage)

		return

	def track_and_update_cpu_usage(self):
		"""Track and update total CPU usage over time for the dashboard."""

		start_time = time.time()
		while True:
			current_time = time.time() - start_time

			# Store time and CPU usage data
			config.times.append(current_time)
			self.get_containers_cpu_usage()

			# Limit the data size for performance (optional)
			if len(config.times) > 100:
				config.times = config.times[1:]
				for container in config.cpu_usages:
					config.cpu_usages[container] = config.cpu_usages[container][1:]

			# Update the plot in Dash
			time.sleep(1)  # Update every second

	def get_containers_memory_usage(self):
		"""Fetch total memory usage for all running containers."""
		self.check_docker_socket()
		#self.client_docker = docker.DockerClient(base_url="unix://var/run/docker.sock")
		network_name = self.docker_network_name

		all_containers = self.client_docker.containers.list(all=True)

		# Identify containers in the target network
		target_containers = []
		for container in all_containers:
			networks = container.attrs['NetworkSettings']['Networks']
			if network_name in networks:
				target_containers.append(container)

		# for now I consider all containers on one machine (all_containers), later we will have cpu usage sum over host machines
		if not 'all_containers' in config.mem_usages:
			config.mem_usages['all_containers'] = []

		total_mem_usage = 0.0
		for container in target_containers:
			container_name = container.name
			try:
				stats = container.stats(stream=False)
				memory_stats = stats.get("memory_stats", {})
				mem_usage = memory_stats.get("usage")
				mem_limit = memory_stats.get("limit")
				print(f'Memory limit for the container is: {mem_limit}')

				if None in (mem_usage, mem_limit) or mem_limit == 0:
					mem_percent = 0.0
				else:
					mem_percent = (mem_usage / mem_limit) * 100.0

				total_mem_usage += mem_percent

				if not container_name in config.mem_usages:
					config.mem_usages[container_name] = []
				config.mem_usages[container_name].append(mem_percent)

			except Exception as e:
				print(f"Error fetching stats for container {container.name}: {e}")

		config.mem_usages['all_containers'].append(total_mem_usage)

		return

	# tocheck
	def track_and_update_memory_usage(self):
		"""Track and update total memory usage over time for the dashboard."""

		start_time = time.time()
		while True:
			current_time = time.time() - start_time

			# Store time and CPU usage data
			config.times.append(current_time)
			self.get_containers_memory_usage()

			# Limit the data size for performance (optional)
			if len(config.times) > 100:
				config.times = config.times[1:]
				for container in config.mem_usages:
					config.mem_usages[container] = config.mem_usages[container][1:]

			# Update the plot in Dash
			time.sleep(1)  # Update every second

	def fetch_container_stats_with_timeout(self, container, timeout=3):
		"""
		Fetch CPU and Memory usage stats from a container with a time limit.
		If the function exceeds `timeout` seconds, it returns None.
		"""
		result = {}

		def get_stats():
			"""Function to fetch stats, runs in a separate thread."""
			try:
				stats = container.stats(stream=False)

				cpu_stats = stats.get("cpu_stats", {})
				precpu_stats = stats.get("precpu_stats", {})

				total_usage = cpu_stats.get("cpu_usage", {}).get("total_usage")
				pre_total_usage = precpu_stats.get("cpu_usage", {}).get("total_usage")
				system_cpu_usage = cpu_stats.get("system_cpu_usage")
				pre_system_cpu_usage = precpu_stats.get("system_cpu_usage")

				if None in (total_usage, pre_total_usage, system_cpu_usage, pre_system_cpu_usage):
					cpu_percent = 0.0
				else:
					cpu_delta = total_usage - pre_total_usage
					system_cpu_delta = system_cpu_usage - pre_system_cpu_usage
					num_cpus = len(cpu_stats.get('cpu_usage', {}).get('percpu_usage', [])) or 1
					cpu_percent = (cpu_delta / system_cpu_delta * num_cpus) * 100.0 if system_cpu_delta > 0 else 0.0

				# Memory Usage
				memory_stats = stats.get("memory_stats", {})
				mem_usage = memory_stats.get("usage")
				mem_limit = memory_stats.get("limit")

				if None in (mem_usage, mem_limit) or mem_limit == 0:
					mem_percent = 0.0
				else:
					mem_percent = (mem_usage / mem_limit) * 100.0

				# Store results
				result["cpu_percent"] = cpu_percent
				result["mem_percent"] = mem_percent
			except Exception as e:
				result["cpu_percent"] = None
				result["mem_percent"] = None
				print(f"Error retrieving stats for container {container.name}: {e}")

		# Start the thread
		stats_thread = threading.Thread(target=get_stats)
		stats_thread.start()
		stats_thread.join(timeout=timeout)  # Wait for the thread to finish, but only up to `timeout` seconds

		if stats_thread.is_alive():
			print(f"Timeout reached for container {container.name}, skipping stats retrieval.")
			return None  # Return None if the function exceeded the time limit

		return result  # Return the collected stats

	def get_network(self):
		try:
			docker_client = docker.from_env()
		except:
			self.logger.info(f"couldn't create client or connect to docker daemon.")
		#docker_client = docker.DockerClient(base_url="unix://var/run/docker.sock")
		network = docker_client.networks.get(self.docker_network_name)
		return network

	def get_connected_containers_info(self):
		network = self.get_network()
		# Get all containers in this network
		containers_info = ""
		print("\nContainers in this network:")
		for container_id, details in network.attrs["Containers"].items():
			container_info = f"  - Container ID: {container_id}, Name: {details['Name']}, IPv4: {details['IPv4Address']}"
			print(container_info)
			containers_info += container_info + '\n'

		return containers_info

	# getting status of zookeeper, workload manager and task manager nodes and their containers.
	def get_nodes_status(self):
		...

	# getting defined BGO DAG info
	def get_bgo_dag(self):
		...

	def run_dashboard(self, containers_info_df, df_znodes_data, znodes_hierarchy_graph_elements, DAG_elements):
		app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

		# Set layout
		app.layout = get_layout()

		# Register callbacks
		register_callbacks(app, containers_info_df, df_znodes_data, znodes_hierarchy_graph_elements, DAG_elements)

		self.logger.info(f"Starting dashboard UI")
		app.run(host='0.0.0.0', port=8050, debug=False)

	# temporarily here
	# tocheck the code
	def explore_znodes(self, path, znodes_data_dic, znodes_hierarchy_graph_nodes, znodes_hierarchy_graph_edges, id_hierarchy_graph = '0', level=0):
		'''
		parent_id_hierarchy: is the id of parent node in the hierarchy graph representation.
		'''
		if path == '/env':return
		#znodes_hierarchy_info = ""
		#self.logger.info("Exploring znodes.")
		indent = "  " * level  # Indentation to visualize hierarchy

		# add node id to znode_hierarchy nodes
		znodes_hierarchy_graph_nodes.append({"data": {"id": id_hierarchy_graph, "label": path}})

		# Get the node data (optional)
		data, stat = self.zk.get(path)
		node_data = ast.literal_eval(data.decode('utf-8')) if data else None

		#self.logger.info(f"data at {path} with type {type(node_data)} is: {data}")

		znodes_data_dic['Path'].append(path)
		if node_data and isinstance(node_data,dict):
			#self.logger.info(f"appending znode with node_data ID {node_data.get('ID')}")
			znodes_data_dic['ID'].append(node_data.get('ID'))
			#self.logger.info(f"Type of descriptor: {type(node_data.get('descriptor'))} and its value is: {node_data.get('descriptor')}")
			znodes_data_dic['Address'].append(node_data.get('descriptor').get('address'))
			znodes_data_dic['Host Name'].append(node_data['descriptor']['host_name'])
			znodes_data_dic['Hardware'].append(node_data['descriptor']['hardware'])
			znodes_data_dic['CPU Cores'].append(node_data['descriptor']['cpu_cores'])
			znodes_data_dic['RAM Size'].append(node_data['descriptor']['ram_size'])
			znodes_data_dic['HDD'].append(node_data['descriptor']['hdd'])
		#elif node_data:
			#self.logger.info('appending znode data with non-dict data.')
			#znodes_data_dic['data'][path] = node_data
		else:
			#self.logger.info('appending znode data with no data.')
			znodes_data_dic['ID'].append('No Data')
			znodes_data_dic['Address'].append('No Data')
			znodes_data_dic['Host Name'].append('No Data')
			znodes_data_dic['Hardware'].append('No Data')
			znodes_data_dic['CPU Cores'].append('No Data')
			znodes_data_dic['RAM Size'].append('No Data')
			znodes_data_dic['HDD'].append('No Data')


		#self.logger.info(f"{indent} - {path} (Data: {node_data}, Children: {stat.numChildren})")


		# Get children and recurse into them
		children = self.zk.get_children(path)

		child_indx = 0
		for child in children:
			child_id_hierarchy_graph = id_hierarchy_graph + str(child_indx)
			child_indx += 1
			znodes_hierarchy_graph_edges.append({"data": {"source": id_hierarchy_graph, "target": child_id_hierarchy_graph}})
			child_path = path.rstrip('/') + '/' + child  # Ensure correct path format
			self.explore_znodes(child_path, znodes_data_dic, znodes_hierarchy_graph_nodes=znodes_hierarchy_graph_nodes, znodes_hierarchy_graph_edges=znodes_hierarchy_graph_edges , level=level + 1, id_hierarchy_graph=child_id_hierarchy_graph)

		return

logging.basicConfig(level=logging.INFO)

def main() -> None:
	try:
		# Initialize logging using our helper
		zookeeper_host = os.environ.get('ZOOKEEPER_HOST', 'zookeeper:2181')
		docker_network_name = 'graphmassivizer_simulation_net'
		dashboard = Dashboard(zookeeper_host, docker_network_name)
		dashboard.logger.debug(f"{os.environ}")
		config.dashboard_obj = dashboard
		dashboard.logger.info("I am Dashboard " + str(dashboard.machine.ID))


		dashboard.logger.info("Initializing Dashboard ... ")

		# some temp code
		#children = dashboard.zk.get_children('/')
		#logger.info("Children ", children)

		# get connected containers info
		#logger.info(dashboard.get_connected_containers_info())
		containers_info_df = dashboard.list_all_containers_info_in_network_multithread()
		print(f'df inside main: columns are: {containers_info_df.columns} and its len is {containers_info_df.shape[0]}')

		dashboard.logger.info(f'{containers_info_df.columns}')

		# Get ZooKeeper host from environment variables
		root_znode_path = '/'
		znodes_data_dic = {'Path':[], 'ID': [], 'Address': [], 'Host Name': [], 'Hardware': [], 'CPU Cores': [], 'RAM Size': [], 'HDD': []}
		znodes_hierarchy_graph_nodes = []
		znodes_hierarchy_graph_edges = []
		dashboard.explore_znodes(root_znode_path, znodes_data_dic, znodes_hierarchy_graph_nodes=znodes_hierarchy_graph_nodes, znodes_hierarchy_graph_edges=znodes_hierarchy_graph_edges)
		df_znodes_data = pd.DataFrame(data=znodes_data_dic)

		dashboard.logger.info(f'znodes hierarchy nodes {znodes_hierarchy_graph_nodes}')
		dashboard.logger.info(f'znodes hierarchy edges {znodes_hierarchy_graph_edges}')

		# Start the background thread for cpu usage histogram
		thread = threading.Thread(target=dashboard.track_and_update_cpu_usage, daemon=True)
		thread.start()

		# Start the background thread for memory usage histogram
		thread = threading.Thread(target=dashboard.track_and_update_memory_usage, daemon=True)
		thread.start()

		# run dashboard
		znodes_hierarchy_graph_elements =  znodes_hierarchy_graph_nodes + znodes_hierarchy_graph_edges
		workflow_DAG_path = './tests/resources/DAG.py-dict'
		#DAG_elements = workflow_DAG_to_graph_elements(workflow_DAG_path)
		dashboard.run_dashboard(containers_info_df, df_znodes_data, znodes_hierarchy_graph_elements, None)

		# Create the dashboard's machine descriptor



		# db_machine_descriptor = create_machine_descriptor(config)

		# Instantiate the InfrastructureManager
		# infrastructure_manager = InfrastructureManager(
		#	 workload_manager=None,  # Replace with actual workload manager instance if available
		#	 zookeeper_host=zookeeper_host,
		#	 wm_machine_descriptor=wm_machine_descriptor,
		#	 config=config
		# )

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


if __name__ == '__main__':
	main()
