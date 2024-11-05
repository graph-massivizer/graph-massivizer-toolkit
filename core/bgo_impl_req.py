from .graph_handle import GraphHandle
from .hardware import Hardware
from .message import Message

class BGOImplReq():
    def __init__(self, gf):
        self.name = "BGO-impl-req"
        self.gf = gf

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            gf=data["gf"],
        )
        return instance

    def to_message(self):
        payload = {
            "name": self.name,
            "gf": self.gf,
        }
        return Message(self.name, payload)

    @classmethod
    def from_message(cls, message):
        return cls.from_dict(message.payload)

