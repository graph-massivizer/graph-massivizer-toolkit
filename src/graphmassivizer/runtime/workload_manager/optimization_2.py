# this contains the optimization parts from the greenifier, the optimizer is in optimization_1
import random

class Optimizer_2:
	def get_greenified_plans_for_bgos(G):
		for node in G.nodes:
			hardware_ids = sorted(list(G.nodes[node]['optimized'].keys()))

	def algorithmsInDAG(DAG):
		return [y for x in DAG['nodes'].values() for y in x['implementations'].values()]

	def optimize(DAG):
		for algMetadata in Optimizer_2.algorithmsInDAG(DAG):
			greenVals = [x['hardware_ID'] for x in sorted(algMetadata['optimized'],key=lambda x: x['cost_energy']+x['cost_time'])]
			algMetadata['greenified']={'1': greenVals[0], '2': greenVals[1], '3': greenVals[random.randint(0, 1)]}
