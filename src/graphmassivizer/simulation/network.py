import logging
from typing import Optional
import docker
import time

from graphmassivizer.simulation.cluster import Cluster
from graphmassivizer.simulation.node import Node

logger = logging.getLogger()


class Network:
    def __init__(self, latency: float = 0.1, bandwidth: float = 100, network_name: str = 'cluster_net') -> None:
        self.latency = latency
        self.bandwidth = bandwidth
        self.cluster: Optional[Cluster] = None
        self.nodes: dict[str, Node] = {}
        self.docker_client = docker.from_env()
        self.network_name = network_name
        self.ensure_network()

    def ensure_network(self) -> None:
        try:
            self.docker_client.networks.get(self.network_name)
            logger.debug(f"Network '{self.network_name}' already exists.")
        except docker.errors.NotFound:
            self.docker_client.networks.create(
                self.network_name, driver="bridge")
            logger.debug(f"Network '{self.network_name}' created.")

    def register_node(self, node: Node) -> None:
        self.nodes[node.node_id] = node

    def register_cluster(self, cluster: Cluster) -> None:
        self.cluster = cluster

    def send_message(self, sender_id: str, receiver_id: str, message: str) -> None:
        time.sleep(self.latency)
        if receiver_id == 'cluster_manager':
            self.cluster.receive_message(message)
        elif receiver_id in self.nodes:
            self.nodes[receiver_id].receive_message(message)
        else:
            print(
                f"Message from {sender_id} to {receiver_id} lost (receiver not found).")
