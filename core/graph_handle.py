class GraphHandle:
    def __init__(self, graph_id=None):
        self.graph_id = graph_id

    def __repr__(self):
        return f"GraphHandle(graph_id={self.graph_id})"

    def to_dict(self):
        return {
            "id": self.graph_id
        }
