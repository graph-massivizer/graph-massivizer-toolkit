from graphmassivizer.runtime.task_manager.input.userInputHandler import UserInputHandler
from graphmassivizer.runtime.workload_manager.parallelizer import Parallelizer
from graphmassivizer.runtime.workload_manager.optimization_1 import Optimizer_1
from graphmassivizer.runtime.workload_manager.optimization_2 import Optimizer_2
import graphmassivizer.runtime.task_manager.BGO.networkx_bgos

from functools import reduce
import inspect, sys

class InputPipeline:

	def __init__(self,
				 metaphactoryAddress="http://localhost:10214/",
				 workflowIRI="https://ontologies.metaphacts.com/bgo-ontology/instances/workflow-deae5723-dafb-4e79-8648-0510f0312958",
				 availableBGOs={x[1].implementationId:{'name':x[0],'class':x[1]} for x in inspect.getmembers(sys.modules['graphmassivizer.runtime.task_manager.BGO.networkx_bgos'], inspect.isclass) if x[0] != "BGO"}):
		self.userInputHandler = UserInputHandler(metaphactoryAddress)
		self.workflowIRI = workflowIRI
		self.availableBGOs = availableBGOs

	def composeDAG(self):

		DAG = self.userInputHandler.getWorkflow(self.workflowIRI,self.availableBGOs)

		firstTask = reduce(lambda x,y: y if y[1]['first'] == True else x,DAG['nodes'].items(),None)[1]

		Parallelizer.parallelize(DAG)

		Optimizer_1.optimize(DAG)

		Optimizer_2.optimize(DAG)

		return DAG,firstTask
