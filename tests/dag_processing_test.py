#import matplotlib.pyplot as plt
import json
import networkx as nx
import re
from networkx.readwrite import json_graph
import sys, os, inspect
from unittest import TestCase
from functools import reduce,partial
import pathlib
import requests
import pickle

from graphmassivizer.runtime.workload_manager.parallelizer import Parallelizer
from graphmassivizer.runtime.workload_manager.optimization_1 import Optimizer_1
from graphmassivizer.runtime.workload_manager.optimization_2 import Optimizer_2
import graphmassivizer.runtime.task_manager.BGO.networkx_bgos

class DAGTest(TestCase):
 inputPath = './tests/resources/subgraph.nt'  
 inputEdgelist = './tests/resources/subgraph.el'  
 ioFile = './tests/resources/graph'
 BGOArgs = {'inputNode':'A5006947708'}

 def getUserInput():
  f = open("./tests/resources/workflow.json")
  queryResult = json.load(f)
  DAG = {"directed": False, "multigraph": False, "graph":DAGTest.formatIRI(queryResult['results']['bindings'][0]['graph']['value']), "nodes":{}, "edges":{} } # need to determine source of the graph metadata

  for queryItem in queryResult['results']['bindings']:

   id = DAGTest.formatIRI(queryItem["task"]['value'])

   if id in DAG['nodes']:
    DAG['nodes'][id]["implementationIds"][DAGTest.formatIRI(queryItem["algorithm"]['value'])] = None
    DAG['nodes'][id]["next"].add(DAGTest.formatIRI(queryItem["next"]['value']))
    continue

   node = {}

   DAG['nodes'][id] = node

   node["bgo"] = DAGTest.formatIRI(queryItem["bgo"]['value'])
   node["implementationIds"] = {DAGTest.formatIRI(queryItem["algorithm"]['value']):None}
   node["first"] = True if queryItem["first"]['value'] == 'true' else False

   if "next" in queryItem:
    node["next"] = {DAGTest.formatIRI(queryItem["next"]['value'])}
    DAG['edges'][id] = node["next"]

  f.close()

  return DAG

 def addKeyAndReturnDict(val,d,k):
  d[k] = getattr(val,k)
  return d

 def formatIRI(iriString):
  return re.split(r"/",iriString)[-1]

 def fetchMetadata(self,cl):
  return reduce(partial(DAGTest.addKeyAndReturnDict,cl),list(filter(lambda x: x[0] != '_' and not callable(x),dir(cl))), {})

 def associateDAGWithAvalableFunctions(DAG,availableBGOs):
  for id,node in DAG['nodes'].items():
   rems = []
   for impId in node['implementationIds']:
    for name,BGO in availableBGOs.items():
     if BGO['implementationId'] == impId:
      node['implementationIds'][impId] = BGO
      break
    if not node['implementationIds'][impId]: rems.append(impId) #check for and remove impossible algorithms
   for rem in rems: node['implementationIds'].pop(rem,None)

  return DAG

 def choreograph(self,DAG,task,init=None):

  firstAvailableTaskAlgorithm = list(task['implementationIds'].values())[0] 

  #Run task
  taskClassInstance = firstAvailableTaskAlgorithm['class'](init if init else pathlib.Path(self.ioFile),pathlib.Path(self.ioFile))
  taskClassInstance.run(self.BGOArgs)

  # check if more tasks
  if 'next' not in task: pass
  else:
   for newTask in task['next']:
    self.choreograph(DAG,DAG['nodes'][newTask])

 def updateInputGraph(self):
  headers = {
      'Accept': 'application/n-triples',
      'Content-Type': 'application/x-www-form-urlencoded',
  }

  data = {
      'topic': 'https://semopenalex.org/concept/C41008148',
      'inputAuthor': 'https://semopenalex.org/author/A5006947708',
  }

  response = requests.post('http://localhost:10214/rest/qaas/coauthorGraphQuery', headers=headers, data=data)

  timer = 0
  timewait = 6000
  timeout = 99999999
  while response.status_code == 204:
   time.sleep(timewait)
   timer += timewait
   if timer > timeout: break
   if response.status_code == 200: break

  with open(self.inputPath, "wb") as output:
   pickle.dump(response.content,output)

  with open(self.inputPath, "rb") as input:
   with open(self.inputEdgelist, "w") as output:
    for line in input.readlines():
     k = re.findall(rb"\<([^\>]+)\>",line)
     if len(k) > 0:
      output.write("{} {}\n".format(DAGTest.formatIRI(str(k[0]))[:-1],DAGTest.formatIRI(str(k[2]))[:-1]))

 def test_main(self) -> None:

  bgoClasses = [x for x in inspect.getmembers(sys.modules['graphmassivizer.runtime.task_manager.BGO.networkx_bgos'], inspect.isclass) if x[0] != "BGO"]
  bgoMetadata = {x[0]:dict({"class":x[1]},**self.fetchMetadata(x[1])) for x in bgoClasses}

  userInput = DAGTest.getUserInput()

  parallelization = Parallelizer.parallelize(userInput)

  optimization1 = Optimizer_1.optimize(parallelization)

  optimization2 = Optimizer_2.optimize(optimization1)

  DAG = DAGTest.associateDAGWithAvalableFunctions(optimization2,bgoMetadata)

  first = reduce(lambda x,y: y if y[1]['first'] == True else x,DAG['nodes'].items(),None)[1]
  
  self.updateInputGraph()
  
  print("Start Node: A5006947708")
  self.choreograph(DAG,first,self.inputEdgelist)
