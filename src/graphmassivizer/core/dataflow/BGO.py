from graphmassivizer.core.dataflow.graph_wrapper import GraphWrapper
from abc import ABC, abstractmethod
import networkx as nx

class BGO:
    def execute(self, data_manager, object_handle, dry_run=False):
        """Execute some transformation on the graph and return a new GraphWrapper."""
        output_handle = object_handle.get_outcome_paths(self)

        if not dry_run:
            # TODO: listen to Zk if the data is available.
            # TODO: When available, execute the code below.
            input_graph = data_manager.load_object(object_handle)
            new_graph = self.process_graph(input_graph)
            data_manager.persist_object(GraphWrapper(new_graph, output_handle))
        else:
            print("BGO({}) -> {}".format())

        return output_handle

    @abstractmethod
    def process_graph(self, graph) -> nx.Graph:
        pass
