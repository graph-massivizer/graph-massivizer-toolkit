import requests
import json

class GraphDatabaseConnector:

	def __init__(self,endpoint):
		self.endpoint = endpoint

	def curl(self,headers=None,data=None,checkInterval=10,timeout=6000000):

		with requests.post(self.endpoint, headers=headers, data=data) as response:

			timer = 0
			while response.status_code == 204: # adding hacky wait loop for long processes
				time.sleep(checkInterval)
				timer += checkInterval
				if timer > timeout: break
				if response.status_code == 200: break

			return response.content
