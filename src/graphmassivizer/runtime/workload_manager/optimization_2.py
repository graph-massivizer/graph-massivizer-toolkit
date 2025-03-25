# this contains the optimization parts from the greenifier, the optimizer is in optimization_1
import random

class Optimizer_2:
	def get_greenified_plans_for_bgos(G):
		for node in G.nodes:
			hardware_ids = sorted(list(G.nodes[node]['optimized'].keys()))

	def optimize(DAG):
		for node in DAG['nodes'].values():
			for alg in node['implementations'].values():
				greenVals = [x['hardware_ID'] for x in sorted(alg['optimized'],key=lambda x: x['cost_energy']+x['cost_time'])]
				alg['greenified']={'1': greenVals[0], '2': greenVals[1], '3': greenVals[random.randint(0, 1)]}
