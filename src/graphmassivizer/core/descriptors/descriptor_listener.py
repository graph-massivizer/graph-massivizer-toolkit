from src.graphmassivizer.core.descriptors.descriptors import Descriptor

from abc import ABC, abstractmethod

from src.graphmassivizer.core.zookeeper.zookeeper_state_manager import ZookeeperStateManager


class DescriptorCallback(ABC):

    @abstractmethod
    def get_property_key(self, descriptor: Descriptor):
        pass

    @abstractmethod
    def callback(self, descriptor:Descriptor):
        pass

class DescriptorListener:
    def __init__(self, state_manager: ZookeeperStateManager, descriptor: Descriptor):
        self.state_manager = state_manager
        self.descriptor = descriptor

    def register_callback(self, callback: DescriptorCallback):
        pass
        # TODO register callback to zookeeper for property