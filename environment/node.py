# environment/node.py

import threading
import time
from commons.terminal import Terminal
import docker

class Node(threading.Thread):
    def __init__(self, node_id, resources, network):
        super().__init__()
        self.node_id = node_id
        self.resources = resources
        self.network = network
        self.status = 'idle'
        self.running = True
        self.terminal = Terminal.get_instance()
        self.docker_client = docker.from_env()
        self.containers = []

    def run(self):
        while self.running:
            # Nodes can perform other tasks if needed
            time.sleep(1)

    def deploy_container(self, service_name):
        container_name = f"{service_name}_{self.node_id}"
        image_name = f"{service_name}_image"
        try:
            container = self.docker_client.containers.run(
                image_name,
                detach=True,
                name=container_name,
                network='architecture-stubs_cluster_net',
                environment={'NODE_ID': self.node_id},
                labels={'node': self.node_id}
            )
            self.containers.append(container)
            self.terminal.log(f"Node {self.node_id} started container {container.name}", level='INFO')
        except Exception as e:
            self.terminal.log(f"Error starting container {container_name} on node {self.node_id}: {e}", level='ERROR')

    def shutdown(self):
        self.running = False
        self.status = 'offline'
        # Stop and remove all running containers
        for container in self.containers:
            container.stop()
            container.remove()
        self.containers.clear()

    def report_status(self):
        return {
            'node_id': self.node_id,
            'status': self.status,
            'containers': [c.name for c in self.containers]
        }

    def receive_message(self, message):
        # Implement as needed for non-task-related messages
        pass