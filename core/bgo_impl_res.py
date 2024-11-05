from .message import Message

class BGOImplRes():
    def __init__(self, gf, implementations):
        self.name = "BGO-impl-res"
        self.gf = gf
        self.implementations = implementations

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            gf=data["gf"],
            implementations=data["implementations"],
        )
        return instance

    def to_message(self):
        payload = {
            "name": self.name,
            "gf": self.gf,
            "implementations": self.implementations,
        }
        return Message(self.name, payload)

    @classmethod
    def from_message(cls, message):
        return cls.from_dict(message.payload)
