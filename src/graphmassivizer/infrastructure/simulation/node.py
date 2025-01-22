from abc import abstractmethod
import json
from threading import Thread
import time
import docker
from docker.models.containers import Container
from kazoo.client import KazooClient

from typing import Any, Optional

from statemachine import State, StateMachine

from graphmassivizer.core.descriptors.descriptors import MachineDescriptor
from graphmassivizer.infrastructure.components import Node, NodeStatus


class SimulatedNode(Node, Thread):
    def __init__(self, node_id: str, machine_info: MachineDescriptor, docker_network_name: str,
                 container_name: str,
                 image_name: str,
                 tag: str

                 ) -> None:
        """network must be of type graphmassivizer.infrastructure.simulation.network import Network
        but we have a cyclic import left
        """
        super().__init__(node_id=node_id)
        Thread.__init__(self)
        self.docker_client = docker.from_env()
        self.container: Optional[Container] = None
        self.machine_info = machine_info
        self.docker_network_name = docker_network_name

        self.__container_name = container_name
        self.__image_name = image_name
        self.__tag = tag

    def run(self) -> None:
        while self.status.current_state == NodeStatus.RUNNING:
            time.sleep(1)

    def _before_deploy(self) -> None:
        pass

    @abstractmethod
    def _get_docker_environment(self) -> dict[str, str]:
        return {}

    def _after_deploy(self) -> None:
        pass

    def deploy(self):
        try:
            container: Container = self.docker_client.containers.run(
                self.__image_name,
                detach=True,
                name=self.__container_name,
                network=self.docker_network_name,  # Correct network name
                environment=self._get_docker_environment(),
                labels={'node': self.node_id}
            )
            self.container = container
        except Exception as e:
            print(f"Error deploying container on node {self.node_id}: {e}")
            raise e

    # def start_zk_client(self) -> None:
    #     try:
    #         self.zk = KazooClient(hosts=self.zookeeper_host)
    #         self.zk.start()
    #     except Exception as e:
    #         print(
    #             f"Error connecting to ZooKeeper from node {self.node_id}: {e}")
    #         raise

    def shutdown(self) -> None:
        if self.status.current_state != NodeStatus.OFFLINE:
            self.status.offline()
            if self.container:
                self.container.stop()
                self.container.remove()
        try:
            existing_container = self.docker_client.containers.get(
                self.__container_name)
            existing_container.stop()
            existing_container.remove()
        except docker.errors.NotFound:
            pass  # No existing container, proceed

    def _report_status(self) -> dict[str, Any]:
        status: dict[str, Any] = {
            'containers': [c.name for c in self.containers]
        }
        # Optionally, you can add more detailed status information
        return status

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

    def collect_machine_info(self) -> MachineDescriptor:
        return self.machine_info

    def receive_message(self, message: str) -> None:
        raise NotImplementedError()


class ZookeeperNode(SimulatedNode):

    def __init__(self, node_id: str, machine_info: MachineDescriptor, docker_network_name: str) -> None:

                self.__container_name = f"zookeeper_{self.node_id}"
        self.__image_name = "zookeeper"
        self.__tag = "3.7"  # Or whatever version you prefer

        super().__init__(node_id, machine_info, docker_network_name)
        self.__zookeeper_environment = {
            'ZOOKEEPER_CLIENT_PORT': '2181',
            'ZOOKEEPER_TICK_TIME': '2000',
            'ZOOKEEPER_INIT_LIMIT': '5',
            'ZOOKEEPER_SYNC_LIMIT': '2',
            'ZOO_4LW_COMMANDS_WHITELIST': '*',
            'KAFKA_OPTS': "-Dzookeeper.4lw.commands.whitelist=*"
        }
        self.__host_port = 2181
        self.zookeeper_host = 'localhost' + str(self.__host_port)

    def deploy_zookeeper(self) -> None:
        """Deploy a Zookeeper instance in Docker."""

        try:
            self.docker_client.images.pull(self.__image_name, tag=self.__tag)
        except Exception as e:
            raise e

        try:
            # Create the container without networking_config
            docker_container = self.docker_client.containers.create(
                self.__image_name + ":" + self.__tag,
                name=self.__container_name,
                hostname='zookeeper',
                detach=True,
                environment=self.__zookeeper_environment,
                # Expose port 2181 for client connections
                ports={'2181/tcp': self.__host_port},
                labels={'node': self.node_id}
            )

            # Connect the container to the network with an alias
            docker_network = self.docker_client.networks.get(
                self.docker_network_name)
            docker_network.connect(docker_container, aliases=['zookeeper'])

            # Start the container
            docker_container.start()

            self.container = docker_container

        except Exception as e:
            print(
                f"Error starting Zookeeper container on node {self.node_id}: {e}")

    def _is_zk_running(self) -> bool:

        command = f'sh -c "echo ruok | nc zookeeper_node-0 2181"'
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
        try:
            existing_container = self.docker_client.containers.get(
                self.__container_name)
            existing_container.stop()
            existing_container.remove()
        except docker.errors.NotFound:
            pass  # No existing container, proceed


class WorkflowManagerNode(SimulatedNode):

    def __init__(self, node_id: str, machine_info: MachineDescriptor, docker_network_name: str) -> None:
        super().__init__(node_id, machine_info, docker_network_name)
        self.__container_name = f"workflow_manager_{self.node_id}"

    def deploy_workflow_manager(self) -> None:
        """Deploy the Workload Manager instance in Docker."""
        image_name = "workflow_manager_image"  # Ensure this image is built
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
            network.connect(container, aliases=['workflow_manager'])
            # Start the container
            container.start()
            self.container = container
            print(
                f"Workflow Manager started on {self.node_id} with container {container.name}")
        except Exception as e:
            print(
                f"Error starting Workload Manager on node {self.node_id}: {e}")

    def shutdown(self) -> None:
        raise NotImplementedError()


class TaskManagerNode(SimulatedNode):
    def __init__(self, node_id: str, machine_info: MachineDescriptor, docker_network_name: str) -> None:
        super().__init__(node_id, machine_info, docker_network_name)
        self.__container_name = f"task_manager_{self.node_id}"

    def deploy_task_manager(self) -> None:
        """Deploy the Task Manager instance in Docker."""
        image_name = "task_manager_image"  # Ensure this image is built and available
        try:

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

    def shutdown(self) -> None:
        super().shutdown()
     # Remove existing container if it exists
        try:
            existing_container = self.docker_client.containers.get(
                container_name)
            existing_container.stop()
            existing_container.remove()
        except docker.errors.NotFound:
            pass  # No existing container, proceed
