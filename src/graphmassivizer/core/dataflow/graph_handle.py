import hashlib
import os

from src.graphmassivizer.core.dataflow import BGO


class GraphHandle:
    def __init__(self, graph_path):
        """Initialize GraphHandle with a base directory.
        :param base_dir: The root directory where graphs are stored.
        """
        self.graph_path = graph_path

    def get_outcome_paths(self, bgo: BGO) -> 'GraphHandle':
        new_graph_path = os.path.join(self.graph_path, self.__get_bgo_directory__(bgo))
        return GraphHandle(new_graph_path)

    def get_graph_path(self) -> str:
        return self.graph_path

    def __get_bgo_directory__(self, bgo):
        """Provides a unique directory name that corresponds the BGO.
        :return: The directory name.
        """
        return hashlib.md5(bgo.__name__.encode()).hexdigest()