from abc import ABC, abstractmethod

class DataManager(ABC):
    # This could be any access point to a graph (e.g. an endpoint for request,s or a path to a file for I/O)
    @property
    @abstractmethod
    def graph_location(self):
        pass

    # Adding new information to the graph
    @abstractmethod
    def create(self):
        pass

    # Reading information from the graph
    @abstractmethod
    def read(self):
        pass

    # Update information in the graph
    @abstractmethod
    def update(self):
        pass

    # Erase information from the graph
    @abstractmethod
    def delete(self):
        pass