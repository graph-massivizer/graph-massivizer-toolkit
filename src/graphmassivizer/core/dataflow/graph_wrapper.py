from src.graphmassivizer.core.dataflow.graph_handle import GraphHandle
import networkx as nx


class GraphWrapper:
    def __init__(self, graph: nx.Graph, graph_handle: GraphHandle):
        self.__graph = graph
        self.__graph_handle = graph_handle

    def get_graph(self):
        return self.__graph

    def get_graph_handle(self):
        return self.__graph_handle