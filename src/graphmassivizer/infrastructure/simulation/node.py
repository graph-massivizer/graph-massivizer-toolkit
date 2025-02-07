import logging
import math
import time
from abc import abstractmethod
from threading import Thread
from typing import Any, Optional

import docker
from docker.models.containers import Container

from graphmassivizer.core.descriptors.descriptors import Machine
from graphmassivizer.infrastructure.components import Node, NodeStatus


class SimulatedNode(Node, Thread):
    def __init__(self, node_id: str, machine_info: Machine, docker_network_name: str,
                 container_name: str,
                 image_name: str,
                 tag: str,
                 ports: dict[str, int | list[int]]
                 ) -> None:
        """network must be of type graphmassivizer.infrastructure.simulation.network import Network
        but we have a cyclic import left
        """
        super().__init__(node_id=node_id)
        Thread.__init__(self)
        self.docker_client = docker.from_env()
        self.docker_container: Optional[Container] = None
        self.machine_info: Machine = machine_info
        self.docker_network_name = docker_network_name

        self.__container_name = container_name
        self.__image_name = image_name
        self.__tag = tag

    def run(self) -> None:
        while self.status.current_state == NodeStatus.RUNNING:
            time.sleep(1)

    @ abstractmethod
    def _get_docker_environment(self) -> dict[str, str]:
        return {}

    def deploy(self) -> None:
        
        try:
            self.docker_container = self.docker_client.containers.run(
                self.__image_name + ":" + self.__tag,
                detach=True,
                name=self.__container_name,
                network=self.docker_network_name,
                environment=self._get_docker_environment(),
                labels={'node': self.node_id}
            )
            # TODO In the past we added some aliases as well. Are they still needed?

            # Start the container
            self.docker_container.start()
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
            if self.docker_container:
                self.docker_container.stop()
                self.docker_container.remove()
                del self.docker_container
        # TODO the following ensures that the container is removed, even if we somehow lost connection to it. Is this needed?
        try:
            existing_container = self.docker_client.containers.get(
                self.__container_name)
            existing_container.stop()
            existing_container.remove()
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
        node_id: str,
        machine_info: Machine,
        zookeeper_host: str = "zookeeper"
    ) -> dict[str, str]:
        """
        Returns environment variables for either a Task Manager or a Workflow Manager,
        depending on `role` ('task_manager' or 'workflow_manager').
        """
        # Common to both roles:
        env = {
            "ROLE": role,
            "ZOOKEEPER_HOST": zookeeper_host,
            "NODE_ID": node_id,
        }

        # If you need separate fields for Task vs. Workflow,
        # handle them conditionally:
        if role == "task_manager":
            env["TM_ADDR"] = machine_info.descriptor.address
            env["TM_HOSTNAME"] = machine_info.descriptor.host_name
            env["TM_CPU_CORES"] = str(machine_info.descriptor.cpu_cores)
            env["TM_RAM_SIZE"] = str(machine_info.descriptor.ram_size)
            env["TM_HDD_SIZE"] = str(machine_info.descriptor.hdd)
        elif role == "workflow_manager":
            env["WM_ADDR"] = machine_info.descriptor.address
            env["WM_HOSTNAME"] = machine_info.descriptor.host_name
            env["WM_CPU_CORES"] = str(machine_info.descriptor.cpu_cores)
            env["WM_RAM_SIZE"] = str(machine_info.descriptor.ram_size)
            env["WM_HDD_SIZE"] = str(machine_info.descriptor.hdd)

        return env


class ZookeeperNode(SimulatedNode):

    def __init__(self, node_id: str, machine_info: Machine, docker_network_name: str) -> None:

        self.__container_name = "zookeeper"
        self.__image_name = "zookeeper"
        self.__tag = "3.7"  # Or whatever version you prefer
        self.__host_port = 2181
        super().__init__(node_id, machine_info, docker_network_name,
                         self.__container_name, self.__image_name, self.__tag,
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

        self.zookeeper_host = 'localhost' + str(self.__host_port)

        try:
            self.docker_client.images.pull(self.__image_name, tag=self.__tag)
        except Exception as e:
            raise e

    def _get_docker_environment(self) -> dict[str, str]:
        return self.__zookeeper_environment

    def _is_zk_running(self) -> bool:
        command = f'sh -c "echo ruok | nc {self.__container_name} 2181"'
        try:
            output = self.docker_client.containers.run(
                "alpine:latest",
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


class WorkflowManagerNode(SimulatedNode):

    def __init__(self, node_id: str, machine_info: Machine, docker_network_name: str) -> None:
        self.__container_name = f"workflow_manager_{node_id}"
        print(__name__ + ": CURRENTLY USING ALPINE IMAGE FOR WFM")
        self.__image_name = "gm/runtime"
        self.__tag = "latest"  # Or whatever version you prefer
        
        super().__init__(node_id, 
                         machine_info, 
                         docker_network_name,
                         self.__container_name, 
                         self.__image_name, 
                         self.__tag,
                         {}
                         )
        
        # Use the static helper function
        self.__workflow_manager_environment = SimulatedNode.create_environment(
            role="workflow_manager",
            node_id=node_id,
            machine_info=machine_info,
            zookeeper_host="zookeeper"
        )

    def _get_docker_environment(self) -> dict[str, str]:
        return self.__workflow_manager_environment


class TaskManagerNode(SimulatedNode):
    def __init__(self, node_id: str, machine_info: Machine, docker_network_name: str) -> None:
        self.__container_name = f"task_manager_{node_id}"
        print(__name__ + ": CURRENTLY USING ALPINE IMAGE FOR TM")
        self.__image_name = "gm/runtime"
        self.__tag = "latest"  # Or whatever version you prefer

        super().__init__(node_id, 
                         machine_info, 
                         docker_network_name,
                         self.__container_name, 
                         self.__image_name, 
                         self.__tag,
                         {}
                         )

        self.__task_manager_environment = SimulatedNode.create_environment(
            role="task_manager",
            node_id=node_id,
            machine_info=machine_info,
            zookeeper_host="zookeeper"
        )

    def _get_docker_environment(self) -> dict[str, str]:
        return self.__task_manager_environment

    # def register_task_manager(self) -> None:
    #     node_path = f'/taskmanagers/{self.machine_info.ID}'
    #     data = json.dumps(self.machine_info).encode('utf-8')
    #     assert self.zk
    #     if self.zk.exists(node_path):
    #         self.zk.set(node_path, data)
    #     else:
    #         self.zk.create(node_path, data)
    #     print(f"TaskManager {machine_info['uid']} registered with ZooKeeper.")
