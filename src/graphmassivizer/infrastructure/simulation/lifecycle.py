import logging
import socket
from types import TracebackType
from typing import Any, Optional, Type
from statemachine import Event, State, StateMachine
from graphmassivizer.core.descriptors.descriptors import (Machine, MachineDescriptor)
from graphmassivizer.infrastructure.simulation.cluster import Cluster
from graphmassivizer.infrastructure.simulation.node import (TaskManagerNode, WorkflowManagerNode, ZookeeperNode, HDFSNode)


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

    def after_transition(self, event: Event, state: State) -> None:
        self.logger.info(f"With event {event} to state {state}")


class Simulation:

    def __init__(self, number_of_task_nodes: int) -> None:
        self.number_of_task_nodes = number_of_task_nodes
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        self.state: LifecycleState = LifecycleState()
        self.state.add_listener(LoggingListener(self.logger))  # type: ignore
        self.__machine_descriptor = MachineDescriptor(
            address="",
            host_name=socket.gethostname(),
            hardware="simulated",
            cpu_cores=1,
            ram_size=256,
            hdd=10
        )
        self.__network_name = 'graphmassivizer_simulation_net'

    def __enter__(self) -> "Simulation":
        self.start()
        return self

    def __exit__(self,
                 exctype: Optional[Type[BaseException]],
                 excinst: Optional[BaseException],
                 exctb: Optional[TracebackType]
                 ) -> bool:

        if self.state.current_state not in {LifecycleState.COMPLETED, LifecycleState.FAILED}:
            try:
                self.complete()
            except Exception as e:
                if excinst:
                    raise Exception(
                        "completion failed, but there was an earlier exception that might have caused this.", [e, excinst])
        if excinst:
            print("Closing the server, because an Exception was raised")
            # by returning False, we indicate that the exception was not handled.
            return False
        print("Server closed")
        return True

    def start(self) -> None:

        # We attempt to change the state ahead of doing the action, it will trigger an exception if this is not possible now.
        # TODO consider using the state transition as a trigger to execute the logic.
        self.state.initialize()

        try:

            # create zookeeper
            zookeeper = ZookeeperNode(Machine(0, self.__machine_descriptor), self.__network_name)

            workflow_manager = WorkflowManagerNode(Machine(1, self.__machine_descriptor), self.__network_name)
            
            hdfs_node = HDFSNode(Machine(2, self.__machine_descriptor), self.__network_name)

            # adding the task managers
            task_managers: list[TaskManagerNode] = []
            offset = 3
            for i in range(self.number_of_task_nodes):
                tm = TaskManagerNode(Machine(offset + i, self.__machine_descriptor), self.__network_name)
                task_managers.append(tm)
            self.cluster = Cluster(
                zookeeper, 
                workflow_manager, 
                task_managers, 
                self.__network_name,
                hdfs_node)

        except Exception as e:
            self.state.fail()
            raise e

        self.state.run()
        try:
            self.cluster.ensure_network()

            self.logger.info("deploying all containers")
            zookeeper.deploy()
            self.logger.info("Zookeeper deployed")
            zookeeper.wait_for_zookeeper(10)
            self.logger.info("Zookeeper ready")
            
            # 3. Deploy the HDFS node
            self.__logger.info("Deploying HDFS node...")
            hdfs_node.deploy()
            hdfs_node.wait_for_hdfs(timeout=60)
            self.__logger.info("HDFS node is ready")

            workflow_manager.deploy()
            self.logger.info("Workflow Manager started")

            for tm in task_managers:
                tm.deploy()
                self.logger.info(f"Task Manager started on {tm.node_id}")

        except Exception:
            self.fail()
            raise

        self.logger.info("Full simulation is running...")

    def fail(self) -> None:
        self._try_complete_nodes()
        self.cluster.remove_network()
        if self.state.current_state != LifecycleState.FAILED:
            self.state.fail()

    def complete(self) -> None:
        self.logger.info("Completing the simulation")
        self._try_complete_nodes()
        self.cluster.remove_network()
        if (self.state.current_state != LifecycleState.FAILED):
            self.state.complete()

    def wait_for_completion(self) -> None:
        raise NotImplementedError()

    def _try_complete_nodes(self):
        try:
            self.cluster.zookeeper.shutdown()
            self.logger.info("Zookeeper stopped")
        except Exception as e:
            self.logger.info("Closing the zookeeper failed. " + str(e))
            self.state.fail()
        try:
            self.cluster.workload_manager.shutdown()
            self.logger.info("Workload manager stopped")
        except Exception as e:
            self.logger.info("Closing the workload manager failed. " + str(e))
            self.state.fail()
        for tm in self.cluster.task_managers:
            try:
                tm.shutdown()
                self.logger.info(
                    f"Task manager {tm.node_id} has been shut down.")
            except Exception as e:
                self.logger.info(
                    f"Closing the task manager {tm.node_id} failed. " + str(e))
                self.state.fail()

    def get_status(self) -> tuple[str, list[dict[str, Any]]]:
        # Collect status from the cluster and nodes
        status: tuple[str, list[dict[str, Any]]] = (
            self.state.current_state.id,
            []
        )
        if self.state.current_state in {LifecycleState.CREATED, LifecycleState.RUNNING}:

            for tm in self.cluster.task_managers:
                node_status: dict[str, Any] = tm.report_status()
                status[1].append(node_status)
        return status
