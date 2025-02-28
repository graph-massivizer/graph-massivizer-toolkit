import pathlib
import pickle

import networkx as nx

from graphmassivizer.runtime.task_manager.task_execution_unit import BGO


class ToNetworkX(BGO):
    def __init__(self, input_path: pathlib.Path, output_path: pathlib.Path) -> None:
        self.input_path = input_path
        self.out = output_path

    def run(self):
        input = nx.read_edgelist(self.input_path)
        with open(self.out, "wb") as out:
            pickle.dump(input, out)


class BFS(BGO):
    def __init__(self, root: str, input_path: pathlib.Path, output_path: pathlib.Path) -> None:
        self.root = root
        self.input_path = input_path
        self.out = output_path

    def run(self):
        with open(self.input_path, "rb") as input:
            graph = pickle.load(input)
        bfs_graph = nx.bfs_tree(graph, depth_limit=2)
        with open(self.out, "wb") as out:
            pickle.dump(input, bfs_graph)


class BetweennessCentrality(BGO):
    def __init__(self, input_path: pathlib.Path, output_path: pathlib.Path) -> None:
        self.input_path = input_path
        self.out = output_path

    def run(self):
        with open(self.input_path, "rb") as input:
            bfs_graph = pickle.load(input)
        betweenness = nx.betweenness_centrality(bfs_graph)
        with open(self.out, "wb") as out:
            pickle.dump(betweenness, out)


class FindMax(BGO):
    """Find Max betweenness"""

    def __init__(self, input_path: pathlib.Path, output_path: pathlib.Path) -> None:
        self.input_path = input_path
        self.out = output_path

    def run(self):
        with open(self.input_path, "rb") as input:
            betweenness = pickle.load(input)

        def f(k_v): return k_v[1]
        max_betweenness = max(betweenness.items(), key=f)
        with open(self.out, "wb") as out:
            pickle.dump(max_betweenness, out)
