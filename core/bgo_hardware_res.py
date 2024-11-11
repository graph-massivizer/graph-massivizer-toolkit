from .message import Message

class BGOHardwareResponse():
    def __init__(self, uuid, hardware):
        self.name = "BGO-hardware-res"
        self.uuid = uuid
        self.hardware = hardware

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            uuid=data["uuid"],
            hardware=data["hardware"],
        )
        return instance

    def to_message(self):
        payload = {
            "name": self.name,
            "uuid": self.uuid,
            "hardware": self.hardware
        }
        return Message(self.name, payload)

    @classmethod
    def from_message(cls, message):
        return cls.from_dict(message.payload)
