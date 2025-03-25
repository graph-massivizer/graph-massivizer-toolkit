import json
import re

from graphmassivizer.core.connectors.metaphactory import MetaphactoryConnector

class UserInputHandler:

	def __init__(self,metaphactoryAddress):
		self.metaphactory = MetaphactoryConnector(metaphactoryAddress)
		self.DAG = {"directed": False, "multigraph": False, "graph":None, "nodes":{}, "edges":{}}

	def getWorkflow(self,workflowIRI,availableBGOs):
		return self.formatWorkflow(json.loads(self.metaphactory.workflowQuery(workflowIRI)),workflowIRI,availableBGOs)

	def formatIRI(iriString):
		return re.split(r"/",iriString)[-1]

	def formatWorkflow(self,queryResult,workflowIRI,available):
		self.DAG["graph"] = UserInputHandler.formatIRI(workflowIRI)

		for queryItem in queryResult['results']['bindings']:
			id = UserInputHandler.formatIRI(queryItem["task"]['value'])
			algorithm = UserInputHandler.formatIRI(queryItem["algorithm"]['value'])

			if not any(map(lambda x: algorithm == x,available.keys())): continue # skip unavailable BGOs

			if id in self.DAG['nodes']:
				self.DAG['nodes'][id]['implementations'][algorithm] = {"class":available[algorithm]["class"],"platform":queryItem["platform"]['value'],"sequential":queryItem["sequential"]['value'],"language":queryItem["language"]['value']}
				if "hardwareRequirement" in queryItem:
					self.DAG['nodes'][id]['implementations'][algorithm]["hardwareRequirement"] = UserInputHandler.formatIRI(queryItem["hardwareRequirement"]["value"])
					continue

			node = {}

			self.DAG['nodes'][id] = node

			node["bgo"] = UserInputHandler.formatIRI(queryItem["bgo"]['value'])
			node["first"] = True if queryItem["first"]['value'] == 'true' else False

			node['implementations'] = {algorithm:{"class":available[algorithm]["class"],"platform":queryItem["platform"]['value'],"sequential":queryItem["sequential"]['value'],"language":queryItem["language"]['value']}}
			if "hardwareRequirement" in queryItem:
			 node['implementations'][algorithm]["hardwareRequirement"] = UserInputHandler.formatIRI(queryItem["hardwareRequirement"]["value"])

			if "next" in queryItem:
			 node["next"] = {UserInputHandler.formatIRI(queryItem["next"]['value'])}
			 self.DAG['edges'][id] = node["next"]

		return self.DAG
