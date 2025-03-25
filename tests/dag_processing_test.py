#import matplotlib.pyplot as plt
import json
import networkx as nx
import re
from networkx.readwrite import json_graph
import sys, os, inspect
from unittest import TestCase
from functools import reduce, partial
import pathlib
import requests
import pickle

from graphmassivizer.core.input.preprocessing import InputPipeline

class DAGTest(TestCase):

 inputPath = './tests/resources/subgraph.nt'
 inputEdgelist = './tests/resources/subgraph.el'
 ioFile = './tests/resources/graph'
 BGOArgs = {'inputNode':'A5006947708'}

 def choreograph(self,DAG,task,init=None):

  firstAvailableTaskAlgorithm = list(task['implementations'].values())[0]

  #Run task
  taskClassInstance = firstAvailableTaskAlgorithm['class'](init if init else pathlib.Path(self.ioFile),pathlib.Path(self.ioFile))
  taskClassInstance.run(self.BGOArgs)

  # check if more tasks
  if 'next' not in task: pass
  else:
   for newTask in task['next']:
    self.choreograph(DAG,DAG['nodes'][newTask])

 def updateInputGraph(self,userInputHandler):

  result = userInputHandler.metaphactory.coauthorQuery(topic='https://semopenalex.org/concept/C41008148',author='https://semopenalex.org/author/A5006947708')

  with open(self.inputPath, "wb") as output:
   pickle.dump(result,output)

  with open(self.inputPath, "rb") as input:
   with open(self.inputEdgelist, "w") as output:
    for line in input.readlines():
     k = re.findall(rb"\<([^\>]+)\>",line)
     if len(k) > 0:
      output.write("{} {}\n".format(DAGTest.formatIRI(str(k[0]))[:-1],DAGTest.formatIRI(str(k[2]))[:-1]))

 def test_main(self) -> None:

  inputPipeline = InputPipeline()

  DAG,first = inputPipeline.composeDAG()

  self.updateInputGraph(inputPipeline.userInputHandler)

  print("Start Node: A5006947708")
  self.choreograph(DAG,first,self.inputEdgelist)
