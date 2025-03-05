from kazoo.client import KazooClient
from kazoo.recipe.watchers import ChildrenWatch
from kazoo.recipe.watchers import DataWatch
import time

from src.graphmassivizer.core.descriptors.descriptor_listener import DescriptorListener
from src.graphmassivizer.core.descriptors.descriptors import Descriptor


class ZookeeperStateManager:

    def __init__(self, hosts):
        self.zk = KazooClient(hosts)
        self.zk.start()
        self.watchers = {}

    def __set_node_value(self, path, value):
        self.zk.ensure_path(path)
        self.zk.set(path, value)

    def __get_descriptor_directory(self, descriptor: Descriptor):
        descriptor_id = descriptor.get_id()
        descriptor_class = descriptor.__class__.__name__
        descriptor_category = descriptor.get_descriptor_category()

        return "{}/{}/{}".format(descriptor_category, descriptor_class, descriptor_id)

    def register_descriptor(self, descriptor: Descriptor):
        base_directory = self.__get_descriptor_directory(descriptor)
        descriptor_dict = descriptor.to_dict()
        for key, value in descriptor_dict.items():
            self.__set_node_value(f"{base_directory}/{key}", value.encode())

    def unregister_descriptor(self, descriptor: Descriptor):
        base_directory = self.__get_descriptor_directory(descriptor)
        try:
            self.zk.delete(base_directory, recursive=True)
            print("Node and its children deleted successfully.")
        except Exception as e:
            print(f"Error deleting node: {e}")

    def register_descriptor_listener(self, descriptorListener: DescriptorListener):
        self.watchers[descriptorListener.get_id()] = descriptorListener

    def unregister_descriptor_listener(self, descriptorListener: DescriptorListener):
        self.watchers[descriptorListener.get_id()].set_active(False)


    def stop(self):
        self.zk.stop()
