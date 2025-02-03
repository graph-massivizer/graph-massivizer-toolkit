#import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import sys, os
from unittest import TestCase

from graphmassivizer.runtime.workload_manager.parallelizer import Parallelizer
from graphmassivizer.runtime.workload_manager.optimization_1 import Optimizer_1
from graphmassivizer.runtime.workload_manager.optimization_2 import Optimizer_2

class DAGTest(TestCase):
	"""
	def plot_graph(G):
	    pos = nx.spring_layout(G)
	    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=20, font_size=5)
	    
	    plt.title("Graph")
	    plt.show()
	"""
	def getUserInput():
		df = pd.read_csv('./tests/resources/minimalWorkflow.csv')

		G = nx.Graph()  # Use nx.DiGraph() for directed graphs

		# Add edges with attributes
		for _, row in df.iterrows():
		    G.add_edge(row['s'], row['q'], **row.drop(['s', 'q']).to_dict())
		
		#plot_graph(G)
		
		return G

	def test_main(self) -> None:

		userInput = DAGTest.getUserInput()
		
		parallelization = Parallelizer.parallelize(userInput)
		
		optimization1 = Optimizer_1.optimize(parallelization)
		
		optimization2 = Optimizer_2.optimize(optimization1)
		
		print(f"Scheduled graph:\n{optimization2}")
	

