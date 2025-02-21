from kazoo.client import KazooClient
from kazoo.recipe.watchers import ChildrenWatch
import time

from src.graphmassivizer.core.descriptors.descriptors import Descriptor


class ZookeeperStateManager:

    def __init__(self, hosts):
        self.zk = KazooClient(hosts)
        self.zk.start()

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

    def register_descriptor_listener(self, descriptor: Descriptor):
        descriptor_id = descriptor.get_id()
        base_directory = "{}/{}".format(descriptor.__class__.__name__, descriptor_id)
        descriptor_dict = descriptor.to_dict()
        for key, value in descriptor_dict.items():
            self.__set_node_value(f"{base_directory}/{key}", value.encode())



    def perform_action(self, children):
        print("Children nodes: ", children)

    def watch_znode(self, path):
        ChildrenWatch(self.zk, path, self.perform_action)

    def stop(self):
        self.zk.stop()

def main():
    znode_path = '/our/gm/znode'
    client = MyZkListener('127.0.0.1:2181')
    client.watch_znode()

    client.create_node(znode_path, b'Some data')
    time.sleep(2)  # sleep to make sure listener gets the creation event

    # update node with new data
    client.update_node(znode_path, b'Updated data')
    time.sleep(2)

    try:
        while True:  # keep main thread alive
            pass
    except KeyboardInterrupt:
        client.stop()

if __name__ == "__main__":
    main()