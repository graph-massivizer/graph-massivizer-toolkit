from pathlib import Path
from data_manager import DataManager

class DatasetManagerNTriples(DataManager):
    def __init__(self, path_to_graph_file: Path):
            if not path_to_graph_file.is_file:
                raise Exception("The provided dataset file does not exist")
            if path_to_graph_file.suffixes != [".nt"]:
                raise Exception(f"The dataset file type ({"".join(path_to_graph_file.suffixes)}) does not match the expected type (.nt)")
            
            self._graph_location = path_to_graph_file

    @property
    def graph_location(self) -> Path:
        return self._graph_location
    
    @graph_location.setter
    def graph_location(self, path_to_graph_file: Path) -> None:
        self._graph_location = path_to_graph_file
    
    