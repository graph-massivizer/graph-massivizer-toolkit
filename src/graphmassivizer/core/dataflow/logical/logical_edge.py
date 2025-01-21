class LogicalEdge:
    class TransferType:
        POINT_TO_POINT = 'POINT_TO_POINT'
        ALL_TO_ALL = 'ALL_TO_ALL'

    class EdgeType:
        FORWARD_EDGE = 'FORWARD_EDGE'
        BACKWARD_EDGE = 'BACKWARD_EDGE'

    def __init__(
        self,
        src_node: LogicalNode,
        dst_node: LogicalNode,
        transfer_type: str,
        edge_type: str
    ) -> None:
        self.src_node = src_node
        self.dst_node = dst_node
        self.transfer_type = transfer_type
        self.edge_type = edge_type

    def __repr__(self) -> str:
        return (
            f"Edge({self.src_node.name} -> {self.dst_node.name}, "
            f"transfer_type={self.transfer_type}, edge_type={self.edge_type})"
        )
