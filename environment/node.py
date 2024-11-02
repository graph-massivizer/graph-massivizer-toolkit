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
        self.task_queue = []
        self.running = True
        self.terminal = Terminal.get_instance()
        self.docker_client = docker.from_env()  # Initialize Docker client
        self.containers = []  # Keep track of containers running on this node

    def run(self):
        while self.running:
            if self.task_queue:
                self.status = 'busy'
                task = self.task_queue.pop(0)
                self.process_task(task)
            else:
                self.status = 'idle'
            time.sleep(1)

    def process_task(self, task):
        component_name = task.get('component')
        if component_name:
            self.start_container(component_name, task)
        else:
            # Simulate processing time
            processing_time = task['complexity'] / self.resources['cpu']
            time.sleep(processing_time)
            self.terminal.log(f"Node {self.node_id} completed task {task['id']}", level='INFO')
            self.report_completion(task)

    def start_container(self, component_name, task):
        # Define the image name
        image_name = f"{component_name}-image"
        try:
            # Ensure the image is available
            self.docker_client.images.get(image_name)
        except docker.errors.ImageNotFound:
            self.terminal.log(f"Image {image_name} not found. Building image...", level='INFO')
            # Build the image (assuming Dockerfile is in ./components/{component_name}/)
            self.docker_client.images.build(path=f'./components/{component_name}/', tag=image_name)

        # Run the container
        container = self.docker_client.containers.run(
            image_name,
            detach=True,
            name=f"{component_name}_{task['id']}",
            labels={"node": self.node_id},
            environment=task.get('env', {}),
            # Add more parameters as needed
        )
        self.containers.append(container)
        self.terminal.log(f"Node {self.node_id} started container {container.name} for task {task['id']}", level='INFO')

        # Monitor the container asynchronously
        threading.Thread(target=self.monitor_container, args=(container, task)).start()

    def monitor_container(self, container, task):
        # Wait for the container to finish
        container.wait()
        self.terminal.log(f"Container {container.name} on node {self.node_id} completed task {task['id']}", level='INFO')
        self.report_completion(task)
        # Clean up
        container.remove()
        self.containers.remove(container)

    def report_completion(self, task):
        completion_message = {
            'type': 'task_completion',
            'node_id': self.node_id,
            'task_id': task['id']
        }
        self.network.send_message(self.node_id, 'cluster_manager', completion_message)

    def add_task(self, task):
        self.task_queue.append(task)

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
            'task_queue_length': len(self.task_queue)
        }

    def receive_message(self, message):
        # Implement as needed
        pass