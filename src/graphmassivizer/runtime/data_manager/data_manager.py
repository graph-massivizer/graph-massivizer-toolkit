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

    # An optional method for execution an arbitrary query
    def query(self):
        raise NotImplementedError(
            f"The class {type(self).__name__} (subclass of DataManager) has not implemented the query() method. Implement this method or use any of create(), read(), update() or write() instead."
        )
