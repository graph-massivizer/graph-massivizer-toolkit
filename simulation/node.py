# environment/node.py

import threading
import time
import docker

class Node(threading.Thread):
    def __init__(self, node_id, resources, network):
        super().__init__()
        self.node_id = node_id
        self.resources = resources
        self.network = network
        self.status = 'idle'
        self.running = True
        self.docker_client = docker.from_env()
        self.containers = []

    def run(self):
        while self.running:
            # Nodes can perform other tasks if needed
            time.sleep(1)

    def deploy_container(self, service_name):
        container_name = f"{service_name}_{self.node_id}"
        image_name = f"{service_name}_image"  # Ensure this matches the image name in docker-compose.yml
    
        # Check if a container with the same name already exists and remove it
        try:
            existing_container = self.docker_client.containers.get(container_name)
            existing_container.stop()
            existing_container.remove()
        except docker.errors.NotFound:
            pass  # No existing container, proceed

        # Start the container on 'cluster_net'
        container = self.docker_client.containers.run(
            image_name,
            detach=True,
            name=container_name,
            network='cluster_net',  # Correct network name
            environment={'NODE_ID': self.node_id},
            labels={'node': self.node_id}
        )
        self.containers.append(container)
            
    def shutdown(self):
        try:
            self.running = False
            self.status = 'offline'
            for container in self.containers:
                container.stop()
                container.remove()
            self.containers.clear()
        except Exception as e:
            print(f"Error during shutdown: {e}")

    def report_status(self):
        return {
            'node_id': self.node_id,
            'status': self.status,
            'containers': [c.name for c in self.containers]
        }

    def receive_message(self, message):
        pass