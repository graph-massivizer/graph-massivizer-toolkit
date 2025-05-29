import pathlib
import pickle
import requests
import json
import sys

import networkx as nx

from graphmassivizer.runtime.task_manager.task_execution_unit import BGO

class ToNetworkX(BGO):

 implementationId = "ToNetworkX-2098698b-d086-4a47-9b66-5242a86eabfd"

 def run(args={}):

  args['graph'] = nx.read_edgelist(args['graph'],delimiter=',',create_using=nx.Graph)

  return args['graph']

class BFS(BGO):

 implementationId = "BreadthFirstSearch-3926ab10-2af0-4991-b400-0d9b760d004f"

 def run(args={}):
  if 'inputNode' not in args or 'graph' not in args: return

  args['bfs_graph'] = nx.bfs_tree(args['graph'],source=args['inputNode'],depth_limit=3)

  return args['bfs_graph']

class BetweennessCentrality(BGO):

 implementationId = "BetweennessCentrality-4f76ba77-40be-41de-a79f-95f9230277a5"

 def run(args={}):
  if 'graph' not in args: return

  args['betweenness'] = nx.betweenness_centrality(args['graph'])

  return [x for x in args['betweenness'].items()][:15]

class FindMax(BGO):
 """Find Max betweenness"""

 implementationId = "FindMax-ac2a4cf7-111f-414c-ab6f-8bd15b4c2697"

 def run(args={}):
  if 'inputNode' not in args or 'betweenness' not in args: return

  def f(k_v): return k_v[1]
  args['max_betweenness'] = max(filter(lambda x: x[0] != args['inputNode'],args['betweenness'].items()), key=f)

  return args['max_betweenness']

class FindPath(BGO):

 implementationId = "FindPath-209a050d-3bef-4539-bb78-7780a71b805e"

 def run(args={}):
  if 'inputNode' not in args or 'graph' not in args: return

  args['path'] = nx.shortest_path(args['graph'],source=args['inputNode'],target=args['max_betweenness'][0])

  return args['path']
