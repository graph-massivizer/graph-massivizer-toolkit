# this contains the optimization parts from the greenifier, the optimizer is in optimization_1
import random

class Optimizer_2:
	def get_greenified_plans_for_bgos(G):
		for node in G.nodes:
			hardware_ids = sorted(list(G.nodes[node]['optimized'].keys()))
		
	def optimize(DAG):
    
    # TODO Ana, Duncan, Dante
       # THIS CAN BE STATIC 
		for node in DAG.nodes:
			hardware_ids = sorted(list(DAG.nodes[node]['optimized'].keys()))
			DAG.nodes[node]['greenified']={'1': hardware_ids[0], '2': hardware_ids[1], '3': hardware_ids[random.randint(0, 1)]}
		return DAG
