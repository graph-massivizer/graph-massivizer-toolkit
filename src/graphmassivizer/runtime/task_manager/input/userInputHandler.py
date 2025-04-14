import json
import re
import io

from graphmassivizer.core.connectors.metaphactory import MetaphactoryConnector

class UserInputHandler:

	def __init__(self,
				 metaphactoryAddress="http://localhost:10214/",
				 bgoArgs={'inputNode':'https://semopenalex.org/author/A5006947708','topic':'https://semopenalex.org/concept/C41008148','author':'https://semopenalex.org/author/A5006947708'}):
		self.metaphactory = MetaphactoryConnector(metaphactoryAddress=metaphactoryAddress)
		self.DAG = {"args":bgoArgs, "directed": False, "multigraph": False, "nodes":{}, "edges":{}}
		if 'graph' not in self.DAG['args']:
			self.DAG['args']['graph'] = self.defaultGraph()

	def getWorkflow(self,workflowIRI,availableBGOs):
		return self.formatWorkflow(json.loads(self.metaphactory.workflowQuery(workflowIRI)),workflowIRI,availableBGOs)

	def defaultGraph(self):
		return io.TextIOWrapper(io.BytesIO(self.metaphactory.coauthorQuery(self.DAG['args']['topic'],self.DAG['args']['author'])[17:]))

	def formatIRI(self,iriString):
		return re.split(r"/",iriString)[-1]

	def formatWorkflow(self,queryResult,workflowIRI,availableBGOs):
		#self.DAG["graph"] = self.formatIRI(queryResult['results']['bindings'][0]['graph']['value'])

		for queryItem in queryResult['results']['bindings']:
			id = self.formatIRI(queryItem["task"]['value'])
			algorithm = self.formatIRI(queryItem["algorithm"]['value'])

			if not any(map(lambda x: algorithm == x,availableBGOs.keys())): continue # skip unavailable BGOs

			if id in self.DAG['nodes']:
				self.DAG['nodes'][id]['implementations'][algorithm] = {"class":availableBGOs[algorithm]["class"],"platform":queryItem["platform"]['value'],"sequential":queryItem["sequential"]['value'],"language":queryItem["language"]['value']}
				if "hardwareRequirement" in queryItem:
					self.DAG['nodes'][id]['implementations'][algorithm]["hardwareRequirement"] = self.formatIRI(queryItem["hardwareRequirement"]["value"])
					continue

			node = {}

			self.DAG['nodes'][id] = node

			node["bgo"] = self.formatIRI(queryItem["bgo"]['value'])
			node["first"] = True if queryItem["first"]['value'] == 'true' else False

			node['implementations'] = {algorithm:{"class":availableBGOs[algorithm]["class"],"platform":queryItem["platform"]['value'],"sequential":queryItem["sequential"]['value'],"language":queryItem["language"]['value']}}
			if "hardwareRequirement" in queryItem:
			 node['implementations'][algorithm]["hardwareRequirement"] = self.formatIRI(queryItem["hardwareRequirement"]["value"])

			if "next" in queryItem:
			 node["next"] = {self.formatIRI(queryItem["next"]['value'])}
			 self.DAG['edges'][id] = node["next"]

		return self.DAG
