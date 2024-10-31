# environment/node.py

import threading
import time

class Node(threading.Thread):
    def __init__(self, node_id, resources, network):
        super().__init__()
        self.node_id = node_id
        self.resources = resources
        self.network = network
        self.status = 'idle'
        self.task_queue = []
        self.running = True

    def run(self):
        while self.running:
            if self.task_queue:
                self.status = 'busy'
                task = self.task_queue.pop(0)
                self.process_task(task)
            else:
                self.status = 'idle'
            time.sleep(1)  # Simulate time between checks

    def process_task(self, task):
        # Simulate task processing based on task complexity and node resources
        processing_time = task['complexity'] / self.resources['cpu']
        time.sleep(processing_time)
        print(f"Node {self.node_id} completed task {task['id']}")
        self.report_completion(task)

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

    def report_status(self):
        return {
            'node_id': self.node_id,
            'status': self.status,
            'task_queue_length': len(self.task_queue)
        }