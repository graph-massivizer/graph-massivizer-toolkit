
# this contains the optimization parts from the optimizer, the greenifier is in optimization_2
#BGO selection
import random
import uuid

class Optimizer_1:

	def get_hardware_descriptors():
		return [{
				"ID": "SRV-001",
				"Type": "Physical",
				"CPU": "Intel Xeon Gold 6230, 20 cores",
				"RAM": 256,
				"Storage": [
					{ "Type": "SSD", "Size": 2048, "Interface": "NVMe" },
					{ "Type": "HDD", "Size": 8192, "Interface": "SAS" }
					],
				"Network": { "Bandwidth": "10 Gbps", "Interfaces": 2 },
				"Power": 800,
				"Location": "Rack 1, Unit 5"
			},
			{
				"ID": "SRV-002",
				"Type": "Blade",
				"CPU": "AMD EPYC 7742, 64 cores",
				"RAM": 512,
				"Storage": [
					{ "Type": "NVMe", "Size": 1024 }
					],
				"Network": { "Bandwidth": "25 Gbps", "Interfaces": 4 },
				"Power": 1200,
				"Location": "Rack 2, Unit 3"
			}]

	def get_optimization_result(algorithmDict,hardwareID):
		randValForAlg = {'hardware_ID':hardwareID,'cost_time':random.randint(86645, 6096529),'cost_energy':random.randint(21661, 2580000)}
		if 'optimized' in algorithmDict: algorithmDict['optimized'].append(randValForAlg)
		else: algorithmDict['optimized'] = [randValForAlg]

	def optimize(DAG):

		DAG['available_hardware'] = Optimizer_1.get_hardware_descriptors()

		for taskId,node in DAG['nodes'].items():
			for algId, algMetadata in node['implementations'].items():
				for hardwareData in DAG['available_hardware']:
					Optimizer_1.get_optimization_result(algMetadata,hardwareData['ID'])
