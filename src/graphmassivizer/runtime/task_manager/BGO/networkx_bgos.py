import pathlib
import pickle

import networkx as nx

from graphmassivizer.runtime.task_manager.task_execution_unit import BGO


class ToNetworkX(BGO):

	implementationId = "ToNetworkX-2098698b-d086-4a47-9b66-5242a86eabfd"
	platform = "CPU"
	sequential = True
	language = "Python"

	def __init__(self, input_path: pathlib.Path, output_path: pathlib.Path) -> None:
		self.input_path = input_path
		self.out = output_path

	def run(self):
		#input = nx.read_edgelist(self.input_path)
		with open(self.out, "wb") as out:
			pickle.dump(input, out)


class BFS(BGO):

	implementationId = "BreadthFirstSearch-3926ab10-2af0-4991-b400-0d9b760d004f"
	platform = "CPU"
	sequential = True
	language = "Python"

	def __init__(self, input_path: pathlib.Path, output_path: pathlib.Path) -> None:
		#self.root = root
		self.input_path = input_path
		self.out = output_path

	def run(self):
		with open(self.input_path, "rb") as input:
			graph = pickle.load(input)
		bfs_graph = nx.bfs_tree(graph, depth_limit=2)
		with open(self.out, "wb") as out:
			pickle.dump(input, bfs_graph)


class BetweennessCentrality(BGO):

	implementationId = "BetweennessCentrality-4f76ba77-40be-41de-a79f-95f9230277a5"
	platform = "CPU"
	sequential = True
	language = "Python"

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

	implementationId = "FindMax-ac2a4cf7-111f-414c-ab6f-8bd15b4c2697"
	platform = "CPU"
	sequential = True
	language = "Python"

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

class FindPath(BGO):

	implementationId = "FindPath-209a050d-3bef-4539-bb78-7780a71b805e"
	platform = "CPU"
	sequential = True
	language = "Python"

	def __init__(self, input_path: pathlib.Path, output_path: pathlib.Path) -> None:
		self.input_path = input_path
		self.out = output_path

	def run(self):
		with open(self.input_path, "rb") as input:
			betweenness = pickle.load(input)

		# path code

		with open(self.out, "wb") as out:
			pickle.dump(max_betweenness, out)
