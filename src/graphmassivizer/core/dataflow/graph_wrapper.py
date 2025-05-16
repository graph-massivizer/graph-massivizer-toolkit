import networkx as nx
import hashlib
import json


class GraphWrapper:
    def __init__(self, graph: nx.Graph):
        """Initialize GraphWrapper with a NetworkX graph."""
        # TODO: we are prototyping with NetworkX - replace with adequate abstraction
        self.graph = graph
        self.graph_metadata = self.compute_metadata()

    def compute_metadata(self):
        """Computes a unique ID based on the graph's structure and content."""
        # TODO: this must be reworked - it does not scale
        graph_data = {
            "nodes": sorted(self.graph.nodes()),
            "edges": sorted(self.graph.edges(data=True))  # Include edge attributes if any
        }
        graph_json = json.dumps(graph_data, sort_keys=True)
        return GraphMetadata(hashlib.md5(graph_json.encode()).hexdigest())

    def get_metadata(self):
        """Returns the graph metadata."""
        return self.graph_metadata

    def __eq__(self, other) -> bool:
        """Checks if two GraphWrapper objects are the same based on their ID."""
        if not isinstance(other, GraphWrapper):
            return False
        return self.graph_metadata.graph_id == other.get_metadata().graph_id
