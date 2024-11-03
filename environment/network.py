# environment/network.py

import random
import time

class Network:
    def __init__(self, latency=0.1, bandwidth=100):
        self.latency = latency
        self.bandwidth = bandwidth
        self.cluster = None
        self.nodes = {}

    def register_node(self, node):
        self.nodes[node.node_id] = node

    def register_cluster(self, cluster):
        self.cluster = cluster

    # def send_message(self, sender_id, receiver_id, message):
    #     # Simulate network latency
    #     time.sleep(self.latency)
    #     # Simulate message delivery
    #     if receiver_id == 'cluster_manager':
    #         self.cluster.receive_message(message)
    #     elif receiver_id in self.nodes:
    #         self.nodes[receiver_id].receive_message(message)
    #     else:
    #         print(f"Message from {sender_id} to {receiver_id} lost (receiver not found).")