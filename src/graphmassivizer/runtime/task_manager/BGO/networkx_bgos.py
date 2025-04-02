import pathlib
import pickle
import requests
import json

import networkx as nx

from graphmassivizer.runtime.task_manager.task_execution_unit import BGO

class ToNetworkX(BGO):

 implementationId = "ToNetworkX-2098698b-d086-4a47-9b66-5242a86eabfd"

 def run(hdfs,out='tmp/'+implementationId,args={}):
  print(args)
  args['graph'] = nx.read_edgelist(args['graph'],delimiter=',',create_using=nx.Graph)

  print("NXGraph: {}".format(args['graph']))

  with hdfs.open_output_stream(out) as out:
   out.write(args['graph'])

class BFS(BGO):

 implementationId = "BreadthFirstSearch-3926ab10-2af0-4991-b400-0d9b760d004f"

 def run(hdfs,out='tmp/'+implementationId,args={}):
  if 'inputNode' not in args or 'graph' not in args: return

  args['bfs_graph'] = nx.bfs_tree(args['graph'],source=args['inputNode'],depth_limit=3)
  print("BFS: {}".format(args['bfs_graph']))

  with hdfs.open_output_stream(out) as out:
   out.write(args['bfs_graph'])

class BetweennessCentrality(BGO):

 implementationId = "BetweennessCentrality-4f76ba77-40be-41de-a79f-95f9230277a5"

 def run(hdfs,out='tmp/'+implementationId,args={}):
  if 'graph' not in args: return

  args['betweenness'] = nx.betweenness_centrality(args['graph'])

  print("BetweennessCentrality (truncated): {}".format([x for x in args['betweenness'].items()][:10]))

  with hdfs.open_output_stream(out) as out:
   out.write(args['betweenness'])


class FindMax(BGO):
 """Find Max betweenness"""

 implementationId = "FindMax-ac2a4cf7-111f-414c-ab6f-8bd15b4c2697"

 def run(hdfs,out='tmp/'+implementationId,args={}):
  if 'inputNode' not in args or 'betweenness' not in args: return

  def f(k_v): return k_v[1]
  args['max_betweenness'] = max(filter(lambda x: x[0] != args['inputNode'],args['betweenness'].items()), key=f)

  print("Max: {}".format(args['max_betweenness']))

  with hdfs.open_output_stream(out) as out:
   out.write(args['max_betweenness'])

class FindPath(BGO):

 implementationId = "FindPath-209a050d-3bef-4539-bb78-7780a71b805e"

 def run(hdfs,out='tmp/'+implementationId,args={}):
  if 'inputNode' not in args or 'graph' not in args: return

  args['path'] = nx.shortest_path(args['graph'],source=args['inputNode'],target=args['max_betweenness'][0])
  print("Path: {}".format(args['path']))

  with hdfs.open_output_stream(out) as out:
   out.write(args['path'])
