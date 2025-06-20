import re
from graphmassivizer.core.connectors.graphDatabaseConnector import GraphDatabaseConnector

class MetaphactoryConnector:

	coauthor = "/rest/qaas/coauthorGraphQuery"
	workflow = "/rest/qaas/workflowQuery"

	def __init__(self,metaphactoryAddress="http://localhost:10214/"):
		self.metaphactoryAddress = metaphactoryAddress
		self.endpoints = {self.coauthor:GraphDatabaseConnector(self.metaphactoryAddress+self.coauthor),self.workflow:GraphDatabaseConnector(self.metaphactoryAddress+self.workflow)}

	def workflowQuery(self,IRI):
		headers = {
			'Accept': 'application/x-turtle',
			'Content-Type': 'application/x-www-form-urlencoded',
		}

		data = {
			'graph': IRI,
		}
		return self.endpoints[self.workflow].curl(headers,data)

	def coauthorQuery(self,topic,author):
		headers = {
			'Accept': 'text/csv',
			'Content-Type': 'application/x-www-form-urlencoded',
		}

		data = {
			'topic': topic,
			'inputAuthor': author,
		}

		return self.endpoints[self.coauthor].curl(headers,data)
