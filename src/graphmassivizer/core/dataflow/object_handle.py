import hashlib
import os

from graphmassivizer.core.dataflow import BGO


class ObjectHandle:
    def __init__(self, object_path):
        """Initialize GraphHandle with a base directory.
        :param base_dir: The root directory where graphs are stored.
        """
        self.object_path = object_path

    def get_outcome_paths(self, bgo: BGO) -> 'ObjectHandle':
        new_graph_path = os.path.join(self.object_path, self.__get_bgo_directory__(bgo))
        return ObjectHandle(new_graph_path)

    def get_object_path(self) -> str:
        return self.object_path

    def __get_bgo_directory__(self, bgo):
        """Provides a unique directory name that corresponds the BGO.
        :return: The directory name.
        """
        return hashlib.md5(bgo.__name__.encode()).hexdigest()
