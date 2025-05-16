from graphmassivizer.core.dataflow.object_handle import ObjectHandle
import networkx as nx


class ObjectWrapper:
    def __init__(self, object: nx.Graph, object_handle: ObjectHandle):
        self.__object = object
        self.object = object_handle

    def get_object(self):
        return self.__object

    def get_object_handle(self):
        return self.object
