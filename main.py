from components.user import User
from components.inceptor import Inceptor
from components.scrutinizer import Scrutinizer
from components.choreographer import Choreographer
from components.optimizer import Optimizer
from components.greenifier import Greenifier
from core.bgo import BGO
from core.message import Message
from core.hardware import Hardware
from core.graph_handle import GraphHandle

import time


from environment.cluster import Cluster
from environment.node import Node
from environment.network import Network

from management.lifecycle_manager import LifecycleManager


def main():
    lifecycle_manager = LifecycleManager()

    # Transition through the FSM states
    lifecycle_manager.initialize_cluster()
    lifecycle_manager.deploy_components()
    lifecycle_manager.receive_job()
    lifecycle_manager.optimize_job()
    lifecycle_manager.optimize_energy()
    lifecycle_manager.provision_resources()
    lifecycle_manager.initialize_runtime()
    lifecycle_manager.execute_job()
    lifecycle_manager.terminate()
    lifecycle_manager.reset()  # Optionally reset to Idle state

if __name__ == '__main__':
    main()

# def main():
#     # Initialize network
#     network = Network(latency=0.1, bandwidth=100)

#     # Initialize cluster
#     cluster = Cluster(network)

#     # Create nodes with varying resources
#     node_specs = [
#         {'node_id': 'node1', 'resources': {'cpu': 4, 'memory': 8}},
#         {'node_id': 'node2', 'resources': {'cpu': 2, 'memory': 4}},
#         {'node_id': 'node3', 'resources': {'cpu': 8, 'memory': 16}},
#     ]

#     # Add nodes to the cluster
#     for spec in node_specs:
#         node = Node(spec['node_id'], spec['resources'], network)
#         network.register_node(node)
#         cluster.add_node(node)

#     # Define tasks
#     tasks = [
#         {'id': 'task1', 'complexity': 10},
#         {'id': 'task2', 'complexity': 20},
#         {'id': 'task3', 'complexity': 5},
#     ]

#     # Assign tasks to the cluster
#     for task in tasks:
#         cluster.assign_task(task)

#     # Monitor cluster status
#     for _ in range(5):
#         cluster.monitor_cluster()
#         time.sleep(2)

#     # Shutdown nodes
#     for node_id in list(cluster.nodes.keys()):
#         cluster.remove_node(node_id)

# if __name__ == '__main__':
#     main()
    
    

# def main():
#     user = User()
#     inceptor = Inceptor()
#     scrutinizer = Scrutinizer()
#     choreographer = Choreographer()
#     optimizer = Optimizer()
#     greenifier = Greenifier()

#     user.start_listening()
#     inceptor.start_listening()
#     scrutinizer.start_listening()
#     choreographer.start_listening()
#     optimizer.start_listening()
#     greenifier.start_listening()

#     time.sleep(1)  # Allow listeners to initialize

#     bgo_request = BGO(GraphHandle("input"), "shortest-path", Hardware(hardware_type="GPU", architecture="NVIDIA A100"), GraphHandle("output"))
#     user.emit_message(bgo_request.to_message(), "*")

#     time.sleep(2)  # Allow time for messages to be processed

# if __name__ == "__main__":
#     main()
