import json
import threading
import time
import uuid
import docker
import socket
from docker.models.containers import Container
from kazoo.client import KazooClient
from statemachine import Event, State, StateMachine

from typing import Any, Optional


class NodeStatus(StateMachine):
    CREATED = State(initial=True)
    RUNNING = State()
    IDLE = State()
    OFFLINE = State(final=True)

    run = Event(CREATED.to(RUNNING) | IDLE.to(RUNNING))
    idle = Event(RUNNING.to(IDLE))
    offline = Event(IDLE.to(OFFLINE) | RUNNING.to(
        OFFLINE) | CREATED.to(OFFLINE))


class Node(threading.Thread):
    def __init__(self, node_id: str, resources, network) -> None:
        """network must be of type graphmassivizer.simulation.network import Network 
        but we have a cyclic import left
        """
        super().__init__()
        self.node_id: str = node_id
        self.resources = resources
        self.network = network
        self.status: NodeStatus = NodeStatus()
        self.docker_client = docker.from_env()
        self.containers: list[Container] = []
        self.zookeeper_host = 'localhost:2181'
        self.zk: Optional[KazooClient] = None

    def run(self) -> None:
        while self.status.current_state == NodeStatus.RUNNING:
            time.sleep(1)

    def deploy_container(self, service_name: str) -> None:
        container_name = f"{service_name}_{self.node_id}"
        # Ensure this matches the image name in docker-compose.yml
        image_name = f"{service_name}_image"
        try:
            try:
                existing_container = self.docker_client.containers.get(
                    container_name)
                existing_container.stop()
                existing_container.remove()
            except docker.errors.NotFound:
                pass  # No existing container, proceed

            container: Container = self.docker_client.containers.run(
                image_name,
                detach=True,
                name=container_name,
                network='cluster_net',  # Correct network name
                environment={'NODE_ID': self.node_id},
                labels={'node': self.node_id}
            )
            self.containers.append(container)
        except Exception as e:
            print(f"Error deploying container on node {self.node_id}: {e}")

    def deploy_zookeeper(self) -> None:
        """Deploy a Zookeeper instance in Docker."""
        container_name = f"zookeeper_{self.node_id}"
        image_name = "zookeeper"
        tag = "3.7"  # Or whatever version you prefer

        try:
            self.docker_client.images.pull(image_name, tag=tag)
        except Exception as e:
            raise e

        try:
            try:
                existing_container = self.docker_client.containers.get(
                    container_name)
                existing_container.stop()
                existing_container.remove()
            except docker.errors.NotFound:
                pass  # No existing container, proceed

            # Create the container without networking_config
            container = self.docker_client.containers.create(
                image_name + ":" + tag,
                name=container_name,

                hostname='zookeeper',
                detach=True,
                environment={
                    'ZOOKEEPER_CLIENT_PORT': '2181',
                    'ZOOKEEPER_TICK_TIME': '2000',
                    'ZOOKEEPER_INIT_LIMIT': '5',
                    'ZOOKEEPER_SYNC_LIMIT': '2',
                    'ZOO_4LW_COMMANDS_WHITELIST': '*',
                    'KAFKA_OPTS': "-Dzookeeper.4lw.commands.whitelist=*"
                },
                # Expose port 2181 for client connections
                ports={'2181/tcp': 2181},
                labels={'node': self.node_id}
            )

            # Connect the container to the network with an alias
            network = self.docker_client.networks.get('cluster_net')
            network.connect(container, aliases=['zookeeper'])

            # Start the container
            container.start()

            self.containers.append(container)
            print(
                f"Zookeeper instance started on {self.node_id} with container {container.name}")

        except Exception as e:
            print(
                f"Error starting Zookeeper container on node {self.node_id}: {e}")

    def start_zk_client(self) -> None:
        try:
            self.zk = KazooClient(hosts=self.zookeeper_host)
            self.zk.start()
        except Exception as e:
            print(
                f"Error connecting to ZooKeeper from node {self.node_id}: {e}")
            raise

    def _is_zk_running(self) -> bool:
        command = 'sh -c "echo ruok | nc zookeeper_node-0 2181"'
        try:
            output = self.docker_client.containers.run(
                "alpine:latest",
                command=command,
                network='cluster_net',
                remove=True
            )
            if b'imok' in output:
                return True
            else:
                return False
        except Exception as e:
            raise e

    def wait_for_zookeeper(self) -> None:
        if self._is_zk_running():
            print("ZooKeeper is ready.")
        else:
            raise NotImplementedError(
                "Zookeeper is not ready and no logic tor retry is implemented")

    def shutdown(self) -> None:
        if self.status.current_state != NodeStatus.OFFLINE:
            self.status.offline()
            for container in self.containers:
                container.stop()
                container.remove()
            self.containers.clear()
            self.zk.stop()

    def report_status(self) -> dict[str, Any]:
        # Existing method
        status: dict[str, Any] = {
            'node_id': self.node_id,
            'status': self.status,
            'containers': [c.name for c in self.containers]
        }
        # Optionally, you can add more detailed status information
        return status

    def deploy_workload_manager(self) -> None:
        """Deploy the Workload Manager instance in Docker."""
        container_name = f"workload_manager_{self.node_id}"
        image_name = "workload_manager_image"  # Ensure this image is built
        try:
            try:
                existing_container = self.docker_client.containers.get(
                    container_name)
                existing_container.stop()
                existing_container.remove()
            except docker.errors.NotFound:
                pass

            # Create the container without networking_config
            container = self.docker_client.containers.create(
                image_name,
                name=container_name,
                detach=True,
                environment={
                    'ZOOKEEPER_HOST': 'zookeeper',  # Use the alias set for Zookeeper
                    'NODE_ID': self.node_id
                },
                labels={'node': self.node_id}
            )
            # Connect the container to the network with an alias
            network = self.docker_client.networks.get('cluster_net')
            network.connect(container, aliases=['workload_manager'])
            # Start the container
            container.start()
            self.containers.append(container)
            print(
                f"Workload Manager started on {self.node_id} with container {container.name}")
        except Exception as e:
            print(
                f"Error starting Workload Manager on node {self.node_id}: {e}")

    def deploy_task_manager(self) -> None:
        """Deploy the Task Manager instance in Docker."""
        container_name = f"task_manager_{self.node_id}"
        image_name = "task_manager_image"  # Ensure this image is built and available
        try:
            # Remove existing container if it exists
            try:
                existing_container = self.docker_client.containers.get(
                    container_name)
                existing_container.stop()
                existing_container.remove()
            except docker.errors.NotFound:
                pass  # No existing container, proceed

            # Create and start the container
            container = self.docker_client.containers.create(
                image_name,
                name=container_name,
                detach=True,
                environment={
                    'ZOOKEEPER_HOST': 'zookeeper',  # Use the alias set for Zookeeper
                    'NODE_ID': self.node_id
                },
                labels={'node': self.node_id}
            )
            # Connect to the network
            network = self.docker_client.networks.get('cluster_net')
            network.connect(container, aliases=[
                            f"task_manager_{self.node_id}"])
            container.start()
            self.containers.append(container)
            print(
                f"Task Manager started on {self.node_id} with container {container.name}")
        except Exception as e:
            print(f"Error starting Task Manager on node {self.node_id}: {e}")

    def register_task_manager(self) -> None:
        machine_info = self.collect_machine_info()
        node_path = f'/taskmanagers/{machine_info["uid"]}'
        data = json.dumps(machine_info).encode('utf-8')
        assert self.zk
        if self.zk.exists(node_path):
            self.zk.set(node_path, data)
        else:
            self.zk.create(node_path, data)
        print(f"TaskManager {machine_info['uid']} registered with ZooKeeper.")

    def collect_machine_info(self) -> dict[str, Any]:
        # Replace with actual methods to collect machine info
        machine_info: dict[str, Any] = {
            'uuid': str(uuid.uuid4()),
            'address': socket.gethostbyname(socket.gethostname()),
            'host_name': socket.gethostname(),
            'data_port': 5000,
            'control_port': 5001,
            'cpu_cores': 4,
            'size_of_ram': 8 * 1024 * 1024 * 1024,  # 8 GB
            'size_of_hdd': 256 * 1024 * 1024 * 1024  # 256 GB
        }
        return machine_info

    def receive_message(self, message: str) -> None:
        raise NotImplementedError()
