from .graph_handle import GraphHandle
from .hardware import Hardware
from .message import Message

class BGOInpRes():
    def __init__(self, uuid, gh):
        self.name = "BGO-inp-res"
        self.uuid = uuid
        self.gh = gh

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            uuid=data["uuid"],
            gf=data["gh"],
        )
        return instance

    def to_message(self):
        payload = {
            "name": self.name,
            "uuid": self.uuid,
            "gh": self.gh,
        }
        return Message(self.name, payload)

    @classmethod
    def from_message(cls, message):
        return cls.from_dict(message.payload)

