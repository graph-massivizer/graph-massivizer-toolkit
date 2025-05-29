from abc import ABC, abstractmethod
from typing import Any, final

from statemachine import Event, State, StateMachine

from graphmassivizer.core.descriptors.descriptors import MachineDescriptor

from threading import Event as ThreadingEvent

# Abstraction of a compute node.


class NodeStatus(StateMachine):
    CREATED = State(initial=True)
    READY = State()
    RUNNING = State()
    IDLE = State()
    OFFLINE = State(final=True)

    ready = Event(CREATED.to(READY))
    run = Event(READY.to(RUNNING) | IDLE.to(RUNNING))
    idle = Event(RUNNING.to(IDLE))
    offline = Event(IDLE.to(OFFLINE) | RUNNING.to(
        OFFLINE) | READY.to(OFFLINE) | CREATED.to(OFFLINE))

    ready_event = ThreadingEvent()

    def on_enter_state(self, event, state) -> None:
        if state == self.READY:
            self.ready_event.set()


class Node(ABC):
    """A node is the abstraction of a piece of hardware that can execute things."""

    def __init__(self, node_id: int) -> None:
        """
        """
        self.node_id: int = node_id
        self.status: NodeStatus = NodeStatus()

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError()

    def shutdown(self) -> None:
        if self.status.current_state != NodeStatus.OFFLINE:
            self.status.offline()

    @final
    def report_status(self) -> dict[str, Any]:
        status: dict[str, Any] = {
            'node_id': self.node_id,
            'status': self.status.current_state.id,
        }
        status_of_derived = self._report_status()
        status.update(status_of_derived)
        return status

    @abstractmethod
    def _report_status(self) -> dict[str, Any]:
        raise NotImplementedError()

    def get_node_info(self) -> MachineDescriptor:
        raise NotImplementedError()
