from .graph_handle import GraphHandle
from .hardware import Hardware
from .message import Message

class BGOInpReq():
    def __init__(self, gh):
        self.name = "BGO-inp-req"
        self.gh = gh

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            gh=data["gh"],
        )
        return instance

    def to_message(self):
        payload = {
            "name": self.name,
            "gh": self.gh,
        }
        return Message(self.name, payload)

    @classmethod
    def from_message(cls, message):
        return cls.from_dict(message.payload)

