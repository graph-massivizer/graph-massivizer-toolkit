import uuid
from typing import List, Dict, Any


class LogicalNode:
    def __init__(
        self,
        name: str,
        degree_of_parallelism: int = 1,
        per_worker_parallelism: int = 1,
        properties: Dict[str, Any] = None
    ):
        self.uid = uuid.uuid4()
        self.name = name
        self.degree_of_parallelism = degree_of_parallelism
        self.per_worker_parallelism = per_worker_parallelism
        self.inputs: List['LogicalNode'] = []
        self.outputs: List['LogicalNode'] = []
        self.properties = properties or {}
        self.execution_nodes: Dict[uuid.UUID, 'ExecutionNode'] = {}
        self.is_already_deployed = False

    def add_input(self, node: 'LogicalNode'):
        if node == self:
            raise ValueError("A node cannot be an input to itself.")
        self.inputs.append(node)

    def add_output(self, node: 'LogicalNode'):
        if node == self:
            raise ValueError("A node cannot be an output to itself.")
        self.outputs.append(node)

    def __repr__(self):
        return f"LogicalNode(name={self.name}, uid={self.uid})"
