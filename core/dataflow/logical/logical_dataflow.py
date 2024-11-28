class LogicalDataflow:
    def __init__(self, name: str):
        self.name = name
        self.nodes: Dict[str, LogicalNode] = {}
        self.edges: List[Edge] = []
        self.source_nodes: Dict[str, LogicalNode] = {}
        self.sink_nodes: Dict[str, LogicalNode] = {}

    def add_node(self, node: LogicalNode):
        if node.name in self.nodes:
            raise ValueError(f"Node with name {node.name} already exists.")
        self.nodes[node.name] = node
        self.source_nodes[node.name] = node
        self.sink_nodes[node.name] = node

    def connect_nodes(
        self,
        src_name: str,
        dst_name: str,
        transfer_type: str = Edge.TransferType.POINT_TO_POINT,
        edge_type: str = Edge.EdgeType.FORWARD_EDGE
    ):
        src_node = self.nodes.get(src_name)
        dst_node = self.nodes.get(dst_name)
        if not src_node or not dst_node:
            raise ValueError("Source or destination node not found.")
        edge = Edge(src_node, dst_node, transfer_type, edge_type)
        self.edges.append(edge)
        src_node.add_output(dst_node)
        dst_node.add_input(src_node)
        if dst_name in self.source_nodes:
            del self.source_nodes[dst_name]
        if src_name in self.sink_nodes:
            del self.sink_nodes[src_name]

    def __repr__(self):
        return f"LogicalDataflow(name={self.name}, nodes={list(self.nodes.keys())})"