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
from dash import Dash
from layout import get_layout
from callbacks import register_callbacks
import docker
import stat
import sys
import pandas as pd
from graphmassivizer.runtime.workload_manager.infrastructure_manager import InfrastructureManager
from graphmassivizer.core.descriptors.descriptors import Machine

class Dashboard:

    def __init__(self, zookeeper_host, machine, docker_network_name, logger) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.zookeeper_host = zookeeper_host
        self.machine = machine
        self.zk = KazooClient(hosts=self.zookeeper_host)
        self.zk.start()
        self.register_self()
        self.docker_network_name = docker_network_name
        self.logger = logger
        
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
            self.client_docker = docker.DockerClient(base_url="unix://var/run/docker.sock")

            # Get network details
            network = self.client_docker.networks.get(self.docker_network_name)

            # List connected containers
            containers = network.containers

            print(f"Containers info in network '{self.docker_network_name}':")
            containers_info = {"Container Name": [], "Status": [], "Host Name":[]}
            for container in containers:
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
            
            containers_info_df = pd.DataFrame(data=containers_info)

            return containers_info_df

        except FileNotFoundError as e:
            self.logger.info(f"Error: {e}")
        except PermissionError as e:
            self.logger.info(f"Error: {e}")
            self.logger.info("Try running the container with the correct permissions.")
        except docker.errors.APIError as e:
            self.logger.info(f"Docker API error: {e}")
        except Exception as e:
            self.logger.info(f"Unexpected error: {e}")


    def update_containers_info(self):
        """Updates containers info in a specific Docker network"""
        try:
            # Ensure Docker socket is accessible
            self.check_docker_socket()

            # Get network details
            network = self.client_docker.networks.get(self.docker_network_name)

            # List connected containers
            containers = network.containers

            print(f"Containers info in network '{self.docker_network_name}':")
            containers_info = {"Container Name": [], "Status": [], "Host Name":[]}
            for container in containers:
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
            
            return containers_info

        except FileNotFoundError as e:
            self.logger.info(f"Error: {e}")
        except PermissionError as e:
            self.logger.info(f"Error: {e}")
            self.logger.info("Try running the container with the correct permissions.")
        except docker.errors.APIError as e:
            self.logger.info(f"Docker API error: {e}")
        except Exception as e:
            self.logger.info(f"Unexpected error: {e}")


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

    def run_dashboard(self, containers_info_df):
        app = Dash(__name__)

        # Set layout
        app.layout = get_layout(containers_info_df)

        # Register callbacks
        register_callbacks(app)
        
        app.run_server(host='0.0.0.0', port=8050, debug=False)

logging.basicConfig(level=logging.INFO)

def main() -> None:
    try:
        # Initialize logging using our helper
        logger = logging.getLogger('Dashboard')
        zookeeper_host = os.environ.get('ZOOKEEPER_HOST', 'zookeeper:2181')
        machine = Machine.parse_from_env(prefix="DASHBOARD_")
        docker_network_name = 'graphmassivizer_simulation_net'
        dashboard = Dashboard(zookeeper_host, machine, docker_network_name, logger)
        logger.info("I am Dashboard " + str(machine.ID))
        
        
        logger.info("Starting Dashboard ... YYYYYY")

        # some temp code
        #children = dashboard.zk.get_children('/')
        #logger.info("Children ", children)

        # get connected containers info
        #logger.info(dashboard.get_connected_containers_info())
        containers_info_df = dashboard.list_containers_info_in_network()
        logger.info("%s", containers_info_df)
        # run dashboard
        dashboard.run_dashboard(containers_info_df)

        # Get ZooKeeper host from environment variables
        

        # Create the dashboard's machine descriptor
        
        
        
        # db_machine_descriptor = create_machine_descriptor(config)

        # Instantiate the InfrastructureManager
        # infrastructure_manager = InfrastructureManager(
        #     workload_manager=None,  # Replace with actual workload manager instance if available
        #     zookeeper_host=zookeeper_host,
        #     wm_machine_descriptor=wm_machine_descriptor,
        #     config=config
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
