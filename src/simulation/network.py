import docker


class Network:
    def __init__(self, latency=0.1, bandwidth=100) -> None:
        self.latency = latency
        self.bandwidth = bandwidth
        self.cluster = None
        self.nodes = {}
        self.docker_client = docker.from_env()
        self.network_name = 'cluster_net'
        self.ensure_network()

    def ensure_network(self) -> None:
        try:
            self.docker_client.networks.get(self.network_name)
            self.cluster = None
            print(f"Network '{self.network_name}' already exists.")
        except docker.errors.NotFound:
            self.docker_client.networks.create(self.network_name, driver="bridge")
            print(f"Network '{self.network_name}' created.")

    def register_node(self, node) -> None:
        self.nodes[node.node_id] = node

    def register_cluster(self, cluster) -> None:
        self.cluster = cluster

    def send_message(self, sender_id, receiver_id, message) -> None:
        time.sleep(self.latency)
        if receiver_id == 'cluster_manager':
            self.cluster.receive_message(message)
        elif receiver_id in self.nodes:
            self.nodes[receiver_id].receive_message(message)
        else:
            print(f"Message from {sender_id} to {receiver_id} lost (receiver not found).")
