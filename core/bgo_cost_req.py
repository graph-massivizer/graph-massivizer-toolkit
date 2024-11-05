from .graph_handle import GraphHandle
from .hardware import Hardware
from .message import Message

class BGOCostReq():
    def __init__(self, gf, hardware_list, input_list):
        self.name = "BGO-cost-req"
        self.gf = gf
        self.hardware_list = hardware_list
        self.input_list = input_list

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            gf=data["gf"],
            hardware_list=data["hardware_list"],
            input_list=data["input_list"],
        )
        return instance

    def to_message(self):
        payload = {
            "name": self.name,
            "gf": self.gf,
            "hardware_list": self.hardware_list,
            "input_list": self.input_list,
        }
        return Message(self.name, payload)

    @classmethod
    def from_message(cls, message):
        return cls.from_dict(message.payload)

