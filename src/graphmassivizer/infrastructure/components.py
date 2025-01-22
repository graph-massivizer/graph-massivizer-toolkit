from abc import ABC, abstractmethod
import json
import threading
import time
import uuid
import docker
import socket
from docker.models.containers import Container
from kazoo.client import KazooClient
from statemachine import Event, State, StateMachine

from typing import Any, Optional, final

from graphmassivizer.core.descriptors.descriptors import MachineDescriptor

# Abstraction of a compute node.


class NodeStatus(StateMachine):
    CREATED = State(initial=True)
    RUNNING = State()
    IDLE = State()
    OFFLINE = State(final=True)

    run = Event(CREATED.to(RUNNING) | IDLE.to(RUNNING))
    idle = Event(RUNNING.to(IDLE))
    offline = Event(IDLE.to(OFFLINE) | RUNNING.to(
        OFFLINE) | CREATED.to(OFFLINE))


class Node(ABC):
    """A node is the abstraction of a piece of hardware that can execute things."""

    def __init__(self, node_id: str) -> None:
        """
        """
        self.node_id: str = node_id
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
