from .message import Message

class BGOGreenResponse():
    def __init__(self, uuid, physical_execution_plans):
        self.name = "BGO-green-res"
        self.uuid = uuid
        self.physical_execution_plans = physical_execution_plans

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            uuid=data["uuid"],
            physical_execution_plans=data["physical_execution_plans"],
        )
        return instance

    def to_message(self):
        payload = {
            "name": self.name,
            "uuid": self.uuid,
            "physical_execution_plans": self.physical_execution_plans
        }
        return Message(self.name, payload)

    @classmethod
    def from_message(cls, message):
        return cls.from_dict(message.payload)
