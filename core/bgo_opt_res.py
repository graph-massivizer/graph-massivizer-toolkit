from .graph_handle import GraphHandle
from .hardware import Hardware
from .message import Message

class BGOOptRes():
    def __init__(self, uuid, cost_estimates):
        self.name = "BGO-opt-res"
        self.uuid = uuid
        self.cost_estimates = cost_estimates

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            uuid=data["uuid"],
            cost_estimates=data["cost_estimates"],
        )
        return instance

    def to_message(self):
        payload = {
            "name": self.name,
            "uuid": self.uuid,
            "cost_estimates": self.cost_estimates,
        }
        return Message(self.name, payload)

    @classmethod
    def from_message(cls, message):
        return cls.from_dict(message.payload)

