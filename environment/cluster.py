# environment/cluster.py

class Cluster:
    def __init__(self, network):
        self.nodes = {}
        self.network = network
        self.network.register_cluster(self)

    def add_node(self, node):
        self.nodes[node.node_id] = node
        node.start()
        print(f"Node {node.node_id} added to cluster.")

    def remove_node(self, node_id):
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.shutdown()
            node.join()
            del self.nodes[node_id]
            print(f"Node {node_id} removed from cluster.")

    def assign_task(self, task):
        # Simple scheduling: assign to the node with the shortest queue
        selected_node = min(
            self.nodes.values(),
            key=lambda n: len(n.task_queue) if n.status != 'offline' else float('inf')
        )
        selected_node.add_task(task)
        print(f"Assigned task {task['id']} to node {selected_node.node_id}")

    def receive_message(self, message):
        if message['type'] == 'task_completion':
            print(f"Cluster received completion of task {message['task_id']} from node {message['node_id']}")

    def monitor_cluster(self):
        for node in self.nodes.values():
            status = node.report_status()
            print(f"Node {status['node_id']}: Status {status['status']}, Task Queue Length {status['task_queue_length']}")