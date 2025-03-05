class GraphMetadata:
    def __init__(self, graph_id: str):
        self.graph_id = graph_id

    def get_id(self) -> str:
        """Returns the unique ID of the graph."""
        return self.graph_id
