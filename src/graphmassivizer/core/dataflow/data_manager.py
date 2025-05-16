from graphmassivizer.core.dataflow.object_wrapper import ObjectWrapper
from graphmassivizer.core.dataflow.object_handle import ObjectHandle
import pickle
import os

class DataManager:
	def __init__(self, base_dir: str, fs):
		self.base_dir = base_dir
		self.fs = fs
		self.fs.create(base_dir)

	def __get_object_path__(self, object_handle: ObjectHandle):
		directory = os.path.join(self.base_dir, object_handle.get_object_path())
		os.makedirs(directory, exist_ok=True)
		return os.path.join(directory, "object.pkl")

	def persist_object(self, object_wrapper: ObjectWrapper):
		"""Persist a object to the directory specified by the ObjectHandle."""
		graph_path = self.__get_object_path__(object_wrapper.get_object_handle())
		with self.fs.open_output_stream(graph_path) as f:
			pickle.dump(object_wrapper.get_object(), f)

	def load_object(self, object_handle: ObjectHandle) -> ObjectWrapper:
		"""Load a object from the directory specified by the ObjectHandle."""
		object_path = self.__get_object_path__(object_handle)

		with self.fs.open_input_stream(object_path) as f:
			graph = pickle.load(f)

		return ObjectWrapper(graph, object_handle)
