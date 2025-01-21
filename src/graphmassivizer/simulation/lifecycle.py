import threading
from enum import Enum
from simulation.cluster import Cluster
from simulation.node import Node
from monitoring.server import create_app


class LifecycleState(Enum):
    INITIALIZED = 'INITIALIZED'
    ENVIRONMENT_SETUP = 'ENVIRONMENT_SETUP'
    CLUSTER_CREATED = 'CLUSTER_CREATED'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'


class SimulationLifecycle:
    def __init__(self) -> None:
        self.state = LifecycleState.INITIALIZED

    def transition(self, new_state) -> None:
        if new_state not in LifecycleState:
            raise ValueError(f"Invalid state: {new_state}")
        self.state = new_state
        print(f"State transitioned to: {self.state}")

    # TODO: This is probably not neccessary. See below
    def initialize_environment(self) -> None:
        if self.state == LifecycleState.INITIALIZED:
            print("Initializing environment...")
            # Initialize the environment and deploy Zookeeper
            self.transition(LifecycleState.ENVIRONMENT_SETUP)
        else:
            print("Cannot initialize environment from current state.")

    # TODO: zookeeper deployment should probably be moved to a seperate deployment phase
    def create_cluster(self, network) -> None:
        if self.state == LifecycleState.ENVIRONMENT_SETUP:
            print("Creating cluster with 10 nodes...")
            cluster = Cluster(network)
            self.cluster = cluster

            # First, create node-0 and deploy ZooKeeper
            node_0 = Node(node_id="node-0", resources={}, network=network)
            cluster.add_node(node_0)
            node_0.deploy_zookeeper()
            node_0.wait_for_zookeeper()

            # Start ZooKeeper client on node-0
            # node_0.start_zk_client()

            # Create the remaining 9 nodes
            for i in range(1, 10):
                node = Node(node_id=f"node-{i}", resources={}, network=network)
                cluster.add_node(node)

            # Initialize monitoring component
            self.initialize_monitoring()

            self.transition(LifecycleState.CLUSTER_CREATED)
        else:
            print("Cannot create cluster from current state.")

    def initialize_monitoring(self) -> None:

        # Create the Flask app with the simulation context
        self.app = create_app(self)

        # Run the Flask app in a separate thread
        def run_app():
            self.app.run(host='0.0.0.0', port=5002)

        self.monitoring_thread = threading.Thread(target=run_app)
        self.monitoring_thread.start()
        print("Monitoring web interface started on port 5002.")

    def get_status(self) -> dict:
        # Collect status from the cluster and nodes
        status = {
            'state': self.state.value,
            'nodes': []
        }
        if self.cluster:
            for node in self.cluster.nodes.values():
                node_status = node.report_status()
                status['nodes'].append(node_status)
        return status

    # TODO: workload_manager deployment should probably be moved to a seperate deployment phase

    def start_simulation(self) -> None:
        if self.state == LifecycleState.CLUSTER_CREATED:
            print("Starting workload manager on node-1...")
            cluster = self.cluster  # Use the stored cluster reference
            cluster.nodes["node-1"].deploy_workload_manager()

            print("Starting task managers on remaining nodes...")
            for node_id, node in cluster.nodes.items():
                if node_id not in ["node-0", "node-1"]:  # Skip node-0 (ZooKeeper) and node-1 (Workload Manager)
                    node.deploy_task_manager()

            print("Simulation is running...")
            self.transition(LifecycleState.RUNNING)
        else:
            print("Cannot start simulation from current state.")

    def complete(self) -> None:
        if self.state == LifecycleState.RUNNING:
            print("Simulation completed.")
            self.transition(LifecycleState.COMPLETED)
        else:
            print("Cannot complete simulation from current state.")

    def fail(self) -> None:
        print("Simulation failed.")
        self.transition(LifecycleState.FAILED)
