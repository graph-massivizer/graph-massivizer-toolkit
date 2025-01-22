import logging
from typing import Optional, cast

import docker
from docker.models.networks import Network

from graphmassivizer.infrastructure.simulation.node import (
    TaskManagerNode, WorkflowManagerNode, ZookeeperNode)


class Cluster:

    def __init__(self, zookeeper: ZookeeperNode, workflow_manager: WorkflowManagerNode, task_managers: list[TaskManagerNode], docker_network_name: str) -> None:
        self.zookeeper = zookeeper
        self.workload_manager = workflow_manager
        self.task_managers = task_managers
        self.docker_network_name = docker_network_name
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__docker_client = docker.from_env()

    def _get_network_if_exists(self) -> Network | None:
        networks = self.__docker_client.networks.list()
        for network in networks:
            if network.name == self.docker_network_name:
                return network
        return None

    def ensure_network(self):
        network = self._get_network_if_exists()
        if network is not None:
            self.__logger.info(
                f"Network '{self.docker_network_name}' already exists.")
            return
        self.__docker_client.networks.create(
            self.docker_network_name, driver="bridge")
        self.__logger.info(
            f"Network '{self.docker_network_name}' created.")

    def remove_network(self):
        network = self._get_network_if_exists()
        if network is not None:
            network.remove()
            self.__logger.info(
                f"Network '{self.docker_network_name}' removed.")

    # def monitor_cluster(self) -> None:
    #     for node in self.nodes.values():
    #         status = node.report_status()
    #         print(
    #             f"Node {status['node_id']}: Status {status['status']}, Task Queue Length {status['task_queue_length']}")

    # def receive_message(self, message: str) -> None:
    #     raise NotImplementedError()
