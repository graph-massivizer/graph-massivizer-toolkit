import socket
from typing import Any
from graphmassivizer.core.descriptors.descriptors import MachineDescriptor
from graphmassivizer.infrastructure.simulation.cluster import Cluster
from graphmassivizer.infrastructure.simulation.node import SimulatedNode, WorkflowManagerNode, ZookeeperNode
# from graphmassivizer.monitoring.server import create_app
import logging

from statemachine import Event, StateMachine, State


class LifecycleState(StateMachine):

    CREATED = State(initial=True)
    INITIALIZED = State()
    RUNNING = State()
    FAILED = State(final=True)
    COMPLETED = State(final=True)

    initialize = Event(CREATED.to(INITIALIZED))
    run = Event(INITIALIZED.to(RUNNING))
    fail = Event(RUNNING.to(FAILED))
    complete = Event(RUNNING.to(COMPLETED))


class LoggingListener:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    def on_transition(self, event: Event, state: State) -> None:
        self.logger.info(f"With {event} to {state}")


class Simulation:

    def __init__(self, number_of_task_nodes: int) -> None:
        self.number_of_task_nodes = number_of_task_nodes
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.state: LifecycleState = LifecycleState()
        self.state.add_listener(LoggingListener(self.logger))  # type: ignore

    def start(self) -> None:

        # We attempt to change the state ahead of doing the action, it will trigger an exception if this is not possible now.
        # TODO consider using the state transition as a trigger to execute the logic.
        self.state.initialize()
        try:
            # create zookeeper
            zookeeper = ZookeeperNode(node_id="node-zookeeper", machine_info=MachineDescriptor(
                address="",
                host_name=socket.gethostname(),
                hardware="simulated",
                cpu_cores=1,
                ram_size=256,
                hdd=10
            ))
            zookeeper.deploy_zookeeper()
            zookeeper.wait_for_zookeeper()
            self.logger.info("Zookeeper started")

            workflow_manager = WorkflowManagerNode(node_id="node-workflowmanager", machine_info=MachineDescriptor(
                address="",
                host_name=socket.gethostname(),
                hardware="simulated",
                cpu_cores=1,
                ram_size=256,
                hdd=10
            ))
            workflow_manager.deploy_workflow_manager()
            self.logger.info("workflow manager started")

            # adding the task managers

            for i in range(self.number_of_task_nodes):
                tm =

        except Exception as e:
            self.state.fail()
            raise e

        try:

            print("Creating cluster with 10 nodes...")

            self.cluster = Cluster()

            # Start ZooKeeper client on node-0
            node_0.start_zk_client()

            MachineDescriptor(
                address="",
                host_name=socket.gethostname(),
                hardware="simulated",
                cpu_cores=1,
                ram_size=256,
                hdd=10
            )

            # Create the remaining 9 nodes
            for i in range(1, 10):
                node = SimulatedNode(node_id=f"node-{i}", resources={})
                self.cluster.add_node(node)

        except Exception:
            self.state.fail()
            raise

        # Now that things are setup, start running
        self.state.run()
        try:
            print("Starting workload manager on node-1...")
            cluster = self.cluster  # Use the stored cluster reference
            self.cluster.nodes["node-1"].deploy_workload_manager()

            print("Starting task managers on remaining nodes...")
            for node_id, node in cluster.nodes.items():
                # Skip node-0 (ZooKeeper) and node-1 (Workload Manager)
                if node_id not in ["node-0", "node-1"]:
                    node.deploy_task_manager()

            print("Simulation is running...")

        except Exception:
            self.state.fail()
            raise

    def fail(self) -> None:
        self.state.fail()

    def complete(self) -> None:
        self.state.complete()

    def get_status(self) -> tuple[str, list[dict[str, Any]]]:
        # Collect status from the cluster and nodes
        status: tuple[str, list[dict[str, Any]]] = (
            self.state.current_state.id,
            []
        )
        if self.cluster:
            for node in self.cluster.nodes.values():
                node_status: dict[str, Any] = node.report_status()
                status[1].append(node_status)
        return status
