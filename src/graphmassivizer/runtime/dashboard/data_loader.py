import pandas as pd
import ast
import os
from graphmassivizer.runtime.task_manager.input.preprocessing import InputPipeline

def load_data():
	return pd.read_csv('data.csv')

# tocheck
def workflow_DAG_to_graph_elements():

	data_dict = InputPipeline(metaphactoryAddress=os.environ["METAPHACTORY"]).getWorkflow()

	nodes_ids_maps = {}
	for node_id in data_dict['nodes'].keys():
		nodes_ids_maps[node_id] = data_dict['nodes'][node_id]['bgo']
	nodes = [{"data": {"id": str(node_id), "label": str(data_dict['nodes'][node_id]['bgo']), "url": "http://localhost:10214/resource/bgoi:" + str(node_id), "implementations": data_dict['nodes'][node_id]['implementations']}, "classes": "microservice"} for node_id in data_dict['nodes'].keys()]


	edges_dic = data_dict['edges']
	edges = [{"data": {"source": str(u), "target": str(list(edges_dic[u])[0])}} for u in edges_dic.keys()]

	print(nodes,edges)
	return nodes + edges

if __name__ == '__main__':
	DAG_path = './tests/resources/DAG.py-dict'
	print(workflow_DAG_to_graph_elements())
	print('done')
