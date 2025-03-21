from src.graphmassivizer.core.dataflow.graph_wrapper import GraphWrapper
from src.graphmassivizer.core.dataflow.graph_handle import GraphHandle
import pickle
import os

class DataManager:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def __get_graph_path__(self, graph_handle: GraphHandle):
        directory = os.path.join(self.base_dir, graph_handle.get_graph_path())
        os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, "graph.pkl")

    def persist_graph(self, graph_wrapper: GraphWrapper):
        """Persist a graph to the directory specified by the GraphHandle."""
        graph_path = self.__get_graph_path__(graph_wrapper.get_graph_handle())
        with open(graph_path, "wb") as f:
            pickle.dump(graph_wrapper.get_graph(), f)

    def load_graph(self, graph_handle: GraphHandle) -> GraphWrapper:
        """Load a graph from the directory specified by the GraphHandle."""
        graph_path = self.__get_graph_path__(graph_handle)
        if not os.path.exists(graph_path):
            raise FileNotFoundError(f"Graph file not found: {graph_path}")

        with open(graph_path, "rb") as f:
            graph = pickle.load(f)

        return GraphWrapper(graph, graph_handle)