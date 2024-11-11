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
            time.sleep(1)

    def deploy_container(self, service_name):
        container_name = f"{service_name}_{self.node_id}"
        image_name = f"{service_name}_image"  # Ensure this matches the image name in docker-compose.yml
        try:
            try:
                existing_container = self.docker_client.containers.get(container_name)
                existing_container.stop()
                existing_container.remove()
            except docker.errors.NotFound:
                pass  # No existing container, proceed

            container = self.docker_client.containers.run(
                image_name,
                detach=True,
                name=container_name,
                network='cluster_net',  # Correct network name
                environment={'NODE_ID': self.node_id},
                labels={'node': self.node_id}
            )
            self.containers.append(container)
        except Exception as e:
            print(f"Error deplying container on node {self.node_id}: {e}")
            
    def deploy_zookeeper(self):
        """Deploy a Zookeeper instance in Docker."""
        container_name = f"zookeeper_{self.node_id}"
        image_name = "zookeeper:3.7"  # Or whatever version you prefer

        try:
            try:
                # Stop and remove existing container if it exists
                existing_container = self.docker_client.containers.get(container_name)
                existing_container.stop()
                existing_container.remove()
            except docker.errors.NotFound:
                pass  # No existing container, proceed

            # Deploy a new Zookeeper container
            container = self.docker_client.containers.run(
                image_name,
                detach=True,
                name=container_name,
                network='cluster_net',
                environment={
                    'ZOOKEEPER_CLIENT_PORT': '2181',
                    'ZOOKEEPER_TICK_TIME': '2000',
                    'ZOOKEEPER_INIT_LIMIT': '5',
                    'ZOOKEEPER_SYNC_LIMIT': '2'
                },
                ports={'2181/tcp': 2181},  # Expose port 2181 for client connections
                labels={'node': self.node_id}
            )
            self.containers.append(container)
            print(f"Zookeeper instance started on {self.node_id} with container {container.name}")

        except Exception as e:
            print(f"Error starting Zookeeper container on node {self.node_id}: {e}")

    def shutdown(self):
        self.running = False
        self.status = 'offline'
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
        pass
    
    def deploy_workload_manager(self):
        """Deploy the Workload Manager instance in Docker."""
        container_name = f"workload_manager_{self.node_id}"
        image_name = "workload_manager_image"  # Ensure this image is built
        try:
            # Remove existing container if it exists
            try:
                existing_container = self.docker_client.containers.get(container_name)
                existing_container.stop()
                existing_container.remove()
            except docker.errors.NotFound:
                pass
            container = self.docker_client.containers.run(
                image_name,
                detach=True,
                name=container_name,
                network='cluster_net',
                environment={
                    'ZOOKEEPER_HOST': 'zookeeper_node-0',  # Zookeeper hostname
                    'NODE_ID': self.node_id
                },
                labels={'node': self.node_id}
            )
            self.containers.append(container)
            print(f"Workload Manager started on {self.node_id} with container {container.name}")
        except Exception as e:
            print(f"Error starting Workload Manager on node {self.node_id}: {e}")