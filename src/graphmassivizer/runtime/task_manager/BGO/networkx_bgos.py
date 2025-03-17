import pathlib
import pickle
import requests
import json

import networkx as nx

from graphmassivizer.runtime.task_manager.task_execution_unit import BGO

class ToNetworkX(BGO):

 implementationId = "ToNetworkX-2098698b-d086-4a47-9b66-5242a86eabfd"
 platform = "CPU"
 sequential = True
 language = "Python"

 def __init__(self, input_path: pathlib.Path, output_path: pathlib.Path) -> None:
  
  self.input_path = input_path
  self.out = './tests/resources/'+self.implementationId

 def run(self):
  with open(self.input_path, "rb") as input:
   ingraph = nx.read_edgelist(input)
   print("NXGraph: {}".format(ingraph))
  with open(self.out, "wb") as out:
   pickle.dump(ingraph, out)

class BFS(BGO):

 implementationId = "BreadthFirstSearch-3926ab10-2af0-4991-b400-0d9b760d004f"
 platform = "CPU"
 sequential = True
 language = "Python"

 def __init__(self, input_path: pathlib.Path, output_path: pathlib.Path) -> None:
  self.input_path = './tests/resources/'+ToNetworkX.implementationId
  self.out = './tests/resources/'+self.implementationId

 def run(self):
  with open(self.input_path, "rb") as input:   
   graph = pickle.load(input)
   bfs_graph = nx.bfs_tree(graph,source='A5006947708',depth_limit=3)
   print("BFS: {}".format(bfs_graph))
  with open(self.out, "wb") as out:
   pickle.dump(bfs_graph,out)

class BetweennessCentrality(BGO):

 implementationId = "BetweennessCentrality-4f76ba77-40be-41de-a79f-95f9230277a5"
 platform = "CPU"
 sequential = True
 language = "Python"

 def __init__(self, input_path: pathlib.Path, output_path: pathlib.Path) -> None:
  self.input_path = './tests/resources/'+ToNetworkX.implementationId
  self.out = './tests/resources/'+self.implementationId

 def run(self):
  with open(self.input_path, "rb") as input:
   graph = pickle.load(input)
  betweenness = nx.betweenness_centrality(graph)
  print("BetweennessCentrality (truncated): {}".format([x for x in betweenness.items()][:10]))
  with open(self.out, "wb") as out:
   pickle.dump(betweenness, out)


class FindMax(BGO):
 """Find Max betweenness"""

 implementationId = "FindMax-ac2a4cf7-111f-414c-ab6f-8bd15b4c2697"
 platform = "CPU"
 sequential = True
 language = "Python"

 def __init__(self, input_path: pathlib.Path, output_path: pathlib.Path) -> None:
  self.input_path = './tests/resources/'+BetweennessCentrality.implementationId
  self.out = './tests/resources/'+self.implementationId

 def run(self):
  with open(self.input_path, "rb") as input:
   betweenness = pickle.load(input)

  def f(k_v): return k_v[1]
  max_betweenness = max(betweenness.items(), key=f)
  print("Max: {}".format(max_betweenness))
  with open(self.out, "wb") as out:
   pickle.dump(max_betweenness, out)

class FindPath(BGO):

 implementationId = "FindPath-209a050d-3bef-4539-bb78-7780a71b805e"
 platform = "CPU"
 sequential = True
 language = "Python"

 def __init__(self, input_path: pathlib.Path, output_path: pathlib.Path) -> None:
  self.input_path = './tests/resources/'+FindMax.implementationId
  self.out = './tests/resources/'+self.implementationId

 def run(self):
  with open(self.input_path, "rb") as input:
   max_betweenness = pickle.load(input)

  with open('./tests/resources/'+ToNetworkX.implementationId,"rb") as gf:
   graph = pickle.load(gf)
   path = nx.shortest_path(graph,source='A5006947708',target=max_betweenness[0])
   print("Path: {}".format(path))

  with open(self.out, "wb") as out:
   pickle.dump(path, out)
