import pickle
import os

class DataManager:
	def __init__(self, base_dir: str, fs):
		self.base_dir = base_dir
		self.fs = fs
		self.fs.create(base_dir)
		# includes metadata about persisted graphs such as:
		#{'graph_id':{'path':'', 'nodes':0, 'edges':0, 'generated_bgo': '', 'gen_bgo_input_graph_ids':['','']}}
		self.graphs_metadata = {} 
		self.logger = self.fs.get_logger("DataManager")

	def retrieve_object_path(self, workflow_id: str, job_id:str):
		''' 
		This function retrieves the stored path for the graph previously saved and was generated in
		workflow with id: workflow_id, and job with id: job_id.
		'''
		graph_id = workflow_id + '/' + job_id

		return self.graphs_metadata[graph_id]['path']

	def generate_graph_path(self, workflow_id: str, job_id:str):
		'''
		This function generates a graph path for the output graph of a job with id job_id in a
	    workflow with id workflow_id.
		'''
		graph_id = workflow_id + '/' + job_id
		graph_folder_path = os.path.join(self.base_dir, graph_id)
		graph_path = os.path.join(graph_folder_path, "object.pkl")
		self.graphs_metadata[graph_id] = {}
		self.graphs_metadata[graph_id]['path'] = graph_path

		return graph_path
	

	def lookup(self, workflow_id: str, job_id:str):
		"""
        Return the HDFS path of the graph, if it exists.
        """
		graph_id = workflow_id + '/' + job_id
		path = self.graphs_metadata.get(graph_id).get('path')
		if path:
			self.logger.info(f"Lookup for graph '{graph_id}': {path}")
		else:
			self.logger.warning(f"Graph ID '{graph_id}' not found.")
		return path

if __name__=='__main__':
	pass
