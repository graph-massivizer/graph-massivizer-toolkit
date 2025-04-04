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

from graphmassivizer.runtime.task_manager.input.preprocessing import InputPipeline

class DAGTest(TestCase):

 ioFile = './tests/resources/file'

 def choreograph(self,DAG,task,init=None):

  firstAvailableTaskAlgorithm = list(task['implementations'].values())[0]

  #Run task
  taskClassInstance = firstAvailableTaskAlgorithm['class']()
  taskClassInstance.run(DAG['args'])

  # check if more tasks
  if 'next' not in task: pass
  else:
   for newTask in task['next']:
    self.choreograph(DAG,DAG['nodes'][newTask])

 def test_main(self) -> None:

  inputPipeline = InputPipeline()

  DAG,first = inputPipeline.composeDAG()

  f = open("./tests/resources/DAG.py-dict","w")# DAG ouput for inspection
  f.write(str(DAG))
  f.close()

  print("Start Node: A5006947708")
  self.choreograph(DAG,first)
