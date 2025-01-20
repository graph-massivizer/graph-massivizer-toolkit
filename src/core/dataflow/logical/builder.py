class LogicalDataflowBuilder:
    def __init__(self, name: str):
        self.logical_dataflow = LogicalDataflow(name)

    def add_node(self, node: LogicalNode):
        self.logical_dataflow.add_node(node)
        return self  # Enable method chaining

    def connect(
        self,
        src_name: str,
        dst_name: str,
        transfer_type: str = Edge.TransferType.POINT_TO_POINT,
        edge_type: str = Edge.EdgeType.FORWARD_EDGE
    ):
        self.logical_dataflow.connect_nodes(src_name, dst_name, transfer_type, edge_type)
        return self

    def build(self) -> LogicalDataflow:
        return self.logical_dataflow