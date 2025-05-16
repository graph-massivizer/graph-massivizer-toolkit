
# this contains the optimization parts from the optimizer, the greenifier is in optimization_2
#BGO selection
import random
import uuid

class Optimizer_1:

	hardware_descriptors = [{"ID": "SRV-001",
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
								"Location": "Rack 2, Unit 3"}]

	benchmarks = { "ToNetworkX-2098698b-d086-4a47-9b66-5242a86eabfd": 0.111984,
				   "BreadthFirstSearch-3926ab10-2af0-4991-b400-0d9b760d004f":
						{"A5077235073": 0.010364, "A5056213327": 0.027985, "A5016013306": 0.009904,
						 "A5080187829": 0.010932, "A5109650481": 0.032903, "A5001795601": 0.029335,
						 "A5003105325": 0.013364, "A5043437297": 0.012090, "A5100392487": 0.027989 },
				   "BetweennessCentrality-4f76ba77-40be-41de-a79f-95f9230277a5":
						{"A5077235073": 9.658904, "A5056213327": 9.800965, "A5016013306": 9.818374,
						 "A5080187829": 9.752667, "A5109650481": 9.793182, "A5001795601": 9.310115,
						 "A5003105325": 9.353130, "A5043437297": 9.370320, "A5100392487": 9.761619 },
				   "FindMax-ac2a4cf7-111f-414c-ab6f-8bd15b4c2697":
						{"A5077235073": 0.000714, "A5056213327": 0.000834, "A5016013306": 0.000728,
						 "A5080187829": 0.000697, "A5109650481": 0.000690, "A5001795601": 0.000680,
						 "A5003105325": 0.000603, "A5043437297": 0.000593, "A5100392487": 0.000937 },
				   "FindPath-209a050d-3bef-4539-bb78-7780a71b805e":
						{"A5077235073": 0.000474, "A5056213327": 0.000029, "A5016013306": 0.000028,
						 "A5080187829": 0.000031, "A5109650481": 0.000027, "A5001795601": 0.000033,
						 "A5003105325": 0.000032, "A5043437297": 0.000025, "A5100392487": 0.000030 }}

	def get_optimization_result(alg,algorithmDict,hardwareID):
		valForAlg = Optimizer_1.benchmarks[alg]
		if 'optimized' not in algorithmDict: algorithmDict['optimized'] = {}
		algorithmDict['optimized'][hardwareID] = valForAlg

	def algorithmsInDAG(DAG):
		return {y:z for x in DAG['nodes'].values() for y,z in x['implementations'].items()}

	def optimize(DAG):

		DAG['available_hardware'] = Optimizer_1.hardware_descriptors # replace with code that fetches from environment (see SimulatedNode)

		for alg,algMetadata in Optimizer_1.algorithmsInDAG(DAG).items():
			for hardwareData in DAG['available_hardware']:
				Optimizer_1.get_optimization_result(alg,algMetadata,hardwareData['ID'])
