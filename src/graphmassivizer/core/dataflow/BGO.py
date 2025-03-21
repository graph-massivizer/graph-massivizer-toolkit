from src.graphmassivizer.core.dataflow.graph_wrapper import GraphWrapper
from src.graphmassivizer.core.dataflow.data_manager import DataManager
from src.graphmassivizer.core.dataflow.graph_handle import GraphHandle
from abc import ABC, abstractmethod
import networkx as nx

class BGO:
    def execute(self, data_manager: DataManager, graph_handle: GraphHandle, dry_run=False) -> GraphHandle:
        """Execute some transformation on the graph and return a new GraphWrapper."""
        output_handle = graph_handle.get_outcome_paths(self)

        if not dry_run:
            input_graph = data_manager.load_graph(graph_handle)
            new_graph = self.process_graph(input_graph)
            data_manager.persist_graph(GraphWrapper(new_graph, output_handle))
        else:
            print("BGO({}) -> {}".format())

        return output_handle

    @abstractmethod
    def process_graph(self, graph) -> nx.Graph:
        pass
