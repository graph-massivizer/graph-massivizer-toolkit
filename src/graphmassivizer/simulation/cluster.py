from .node import Node
from .network import Network


class Cluster:
    def __init__(self, network: Network) -> None:
        self.nodes: dict[str, Node] = {}
        self.network = network
        self.network.register_cluster(self)

    def add_node(self, node: Node) -> None:
        self.nodes[node.node_id] = node
        node.start()
        print(f"Node {node.node_id} added to cluster.")

    def remove_node(self, node_id: str) -> None:
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.shutdown()
            node.join()
            del self.nodes[node_id]
            print(f"Node {node_id} removed from cluster.")

    def monitor_cluster(self) -> None:
        for node in self.nodes.values():
            status = node.report_status()
            print(
                f"Node {status['node_id']}: Status {status['status']}, Task Queue Length {status['task_queue_length']}")
