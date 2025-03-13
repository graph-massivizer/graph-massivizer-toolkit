#import matplotlib.pyplot as plt
import json
import networkx as nx
import re
from networkx.readwrite import json_graph
import sys, os, inspect
from unittest import TestCase
from functools import reduce,partial
import pathlib

from graphmassivizer.runtime.workload_manager.parallelizer import Parallelizer
from graphmassivizer.runtime.workload_manager.optimization_1 import Optimizer_1
from graphmassivizer.runtime.workload_manager.optimization_2 import Optimizer_2
import graphmassivizer.runtime.task_manager.BGO.networkx_bgos

class DAGTest(TestCase):


	def getUserInput():
		f = open("./tests/resources/workflow.json")
		queryResult = json.load(f)
		DAG = {"directed": False, "multigraph": False, "graph":DAGTest.formatIRI(queryResult['results']['bindings'][0]['graph']['value']), "nodes":{}, "edges":{} } # need to determine source of the graph metadata

		for queryItem in queryResult['results']['bindings']:

			id = DAGTest.formatIRI(queryItem["task"]['value'])

			if id in DAG['nodes']:
				DAG['nodes'][id]["next"].add(DAGTest.formatIRI(queryItem["next"]['value']))
				continue

			node = {}

			DAG['nodes'][id] = node

			node["bgo"] = DAGTest.formatIRI(queryItem["bgo"]['value'])
			node["implementationId"] = DAGTest.formatIRI(queryItem["algorithm"]['value'])
			node["first"] = queryItem["first"]['value']

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
		bgo = {}
		return reduce(partial(DAGTest.addKeyAndReturnDict,cl),list(filter(lambda x: x[0] != '_' and not callable(x),dir(cl))), bgo)

	def associateDAGWithAvalableFunctions(DAG,availableBGOs):
		for id,node in DAG['nodes'].items():
			for name,BGO in availableBGOs.items():
				if node['implementationId'] == BGO['implementationId']:
					DAG['nodes'][id] = dict(node,**BGO)

		return DAG

	def run2(self,DAG,task):

		#Run task
		taskClassInstance = task['class'](pathlib.Path("in.txt"),pathlib.Path("out.txt"))
		taskClassInstance.run()

		# check if more tasks
		if 'next' not in task:
			pass
		else:
			for newTask in task['next']:
				self.run2(DAG,DAG['nodes'][newTask])


	def test_main(self) -> None:

		bgoClasses = [x for x in inspect.getmembers(sys.modules['graphmassivizer.runtime.task_manager.BGO.networkx_bgos'], inspect.isclass) if x[0] != "BGO"]
		bgoMetadata = {x[0]:dict({"class":x[1]},**self.fetchMetadata(x[1])) for x in bgoClasses}

		userInput = DAGTest.getUserInput()

		parallelization = Parallelizer.parallelize(userInput)

		optimization1 = Optimizer_1.optimize(parallelization)

		optimization2 = Optimizer_2.optimize(optimization1)

		DAG = DAGTest.associateDAGWithAvalableFunctions(optimization2,bgoMetadata)

		first = reduce(lambda x,y: y if y[1]['first'] == True else x,DAG['nodes'].items(),None)[1]

		open("in.txt","w").close()
		self.run2(DAG,first)
