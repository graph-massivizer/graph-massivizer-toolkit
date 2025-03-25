#from graphmassivizer.core.zookeeper.zookeeper_state_manager import ZookeeperStateManager
from graphmassivizer.core.descriptors.descriptors import Descriptor
from kazoo.recipe.watchers import DataWatch
from kazoo.client import KazooClient
from abc import ABC, abstractmethod
import uuid

class DescriptorCallback(ABC):

    def __init__(self):
        self.active = True

    @abstractmethod
    def get_property_key(self, descriptor: Descriptor):
        pass

    def execute(self, data, stat):
        if self.active:
            self.callback(data, stat)

    def set_active(self, active):
        self.active = active

    @abstractmethod
    def callback(self, data, stat):
        pass


class DescriptorListener:
    def __init__(self, descriptor: Descriptor, callback: DescriptorCallback):
        self.descriptor = descriptor
        self.callback = callback
        self.id = str(uuid.uuid4())

    def get_id(self):
        return self.id

    def set_active(self, active):
        self.callback.set_active(active)
