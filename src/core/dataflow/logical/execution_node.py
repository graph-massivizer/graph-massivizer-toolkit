class ExecutionNode:
    def __init__(self, logical_node: LogicalNode, task_index: int):
        self.uid = uuid.uuid4()
        self.logical_node = logical_node
        self.task_index = task_index
        self.state = None  # Placeholder for task state
        self.node_descriptor = None  # Placeholder for node descriptor
        self.node_binding_descriptor = None  # Placeholder for binding descriptor

    def set_state(self, state):
        self.state = state

    def set_node_descriptor(self, descriptor):
        if self.node_descriptor is not None:
            raise ValueError("Node descriptor is already set.")
        self.node_descriptor = descriptor

    def __repr__(self):
        return (
            f"ExecutionNode(uid={self.uid}, "
            f"logical_node={self.logical_node.name}, "
            f"task_index={self.task_index})"
        )