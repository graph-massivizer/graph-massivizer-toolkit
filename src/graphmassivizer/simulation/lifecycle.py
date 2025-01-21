import threading
from graphmassivizer.simulation.cluster import Cluster
from graphmassivizer.simulation.node import Node
from graphmassivizer.monitoring.server import create_app
import logging

from statemachine import Event, StateMachine, State


class LifecycleState(StateMachine):

    CREATE = State(initial=True)
    INITIALIZED = State()
    RUNNING = State()
    FAILED = State(final=True)
    COMPLETED = State(final=True)

    initialize = Event(CREATE.to(INITIALIZED))
    run = Event(INITIALIZED.to(RUNNING))
    fail = Event(RUNNING.to(FAILED))
    complete = Event(RUNNING.to(COMPLETED))


class LoggingListener:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def on_transition(self, event: Event, state: State) -> None:
        self.logger.info(f"With {event} to {state}")


class SimulationLifecycle:

    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.state: LifecycleState = LifecycleState()
        self.state.add_listener(LoggingListener(self.logger))  # type: ignore

    def start(self) -> None:

        self.state.initialize()

        self.state.run()

    def fail(self) -> None:
        self.state.fail()

    def complete(self) -> None:
        self.state.complete()

    # TODO: This is probably not neccessary. See below

    # def initialize_environment(self) -> None:
    #     if self.state == LifecycleState.INITIALIZED:
    #         print("Initializing environment...")
    #         # Initialize the environment and deploy Zookeeper
    #         self.transition(LifecycleState.ENVIRONMENT_SETUP)
    #     else:
    #         print("Cannot initialize environment from current state.")

    # # TODO: zookeeper deployment should probably be moved to a seperate deployment phase
    # def create_cluster(self, network) -> None:
    #     if self.state == LifecycleState.ENVIRONMENT_SETUP:
    #         print("Creating cluster with 10 nodes...")
    #         cluster = Cluster(network)
    #         self.cluster = cluster

    #         # First, create node-0 and deploy ZooKeeper
    #         node_0 = Node(node_id="node-0", resources={}, network=network)
    #         cluster.add_node(node_0)
    #         node_0.deploy_zookeeper()
    #         node_0.wait_for_zookeeper()

    #         # Start ZooKeeper client on node-0
    #         # node_0.start_zk_client()

    #         # Create the remaining 9 nodes
    #         for i in range(1, 10):
    #             node = Node(node_id=f"node-{i}", resources={}, network=network)
    #             cluster.add_node(node)

    #         # Initialize monitoring component
    #         self.initialize_monitoring()

    #         self.transition(LifecycleState.CLUSTER_CREATED)
    #     else:
    #         print("Cannot create cluster from current state.")

    # def initialize_monitoring(self) -> None:

    #     # Create the Flask app with the simulation context
    #     self.app = create_app(self)

    #     # Run the Flask app in a separate thread
    #     def run_app():
    #         self.app.run(host='0.0.0.0', port=5002)

    #     self.monitoring_thread = threading.Thread(target=run_app)
    #     self.monitoring_thread.start()
    #     print("Monitoring web interface started on port 5002.")

    # def get_status(self) -> dict:
    #     # Collect status from the cluster and nodes
    #     status = {
    #         'state': self.state.value,
    #         'nodes': []
    #     }
    #     if self.cluster:
    #         for node in self.cluster.nodes.values():
    #             node_status = node.report_status()
    #             status['nodes'].append(node_status)
    #     return status

    # # TODO: workload_manager deployment should probably be moved to a seperate deployment phase

    # def start_simulation(self) -> None:
    #     if self.state == LifecycleState.CLUSTER_CREATED:
    #         print("Starting workload manager on node-1...")
    #         cluster = self.cluster  # Use the stored cluster reference
    #         cluster.nodes["node-1"].deploy_workload_manager()

    #         print("Starting task managers on remaining nodes...")
    #         for node_id, node in cluster.nodes.items():
    #             # Skip node-0 (ZooKeeper) and node-1 (Workload Manager)
    #             if node_id not in ["node-0", "node-1"]:
    #                 node.deploy_task_manager()

    #         print("Simulation is running...")
    #         self.transition(LifecycleState.RUNNING)
    #     else:
    #         print("Cannot start simulation from current state.")
