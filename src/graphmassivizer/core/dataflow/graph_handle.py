import os
import json
from typing import Any, List, Callable
import hashlib

from src.graphmassivizer.core.dataflow.graph_wrapper import GraphWrapper

import os
from pathlib import Path


class GraphVisitor:
    def __init__(self, bgo):
        """Initializes the GraphVisitor.
        :param bgo: The BGO object that can generate a graph if it doesn't exist.
        """
        self.bgo = bgo

    def compute_graph_path(self, base_dir: str) -> Path:
        """Computes the path where the graph should be stored.

        :param graph_id: Unique identifier for the graph.
        :return: Path object representing the graph file location.
        """
        return os.path.join(base_dir, self.get_bgo_directory())

    def get_bgo_directory(self):
        """Provides a unique directory name that corresponds the BGO.
        :return: The directory name.
        """
        return hashlib.md5(self.bgo.__name__.encode()).hexdigest()

    def load_graph(self, graph_path: Path):
        """Loads a graph from the given path.

        :param graph_path: Path to the stored graph.
        :return: Loaded graph object.
        """




class GraphHandle:
    def __init__(self, graph: GraphWrapper):
        """Initialize GraphHandle with a base directory.
        :param base_dir: The root directory where graphs are stored.
        """
        self.graph = graph
        self.base_dir = self.graph.graph_metadata.graph_id

    def retrieve_graph(self, visitor: GraphVisitor):
        """Retrieve a graph by its ID and visitor criteria.
        :param graph_id: Unique identifier for the graph.
        :param visitor: GraphVisitor
        :return: Graph path as string.
        """
        return visitor.compute_graph_path(self.base_dir)