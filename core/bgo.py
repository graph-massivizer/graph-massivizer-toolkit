import uuid

from .graph_handle import GraphHandle
from .message import Message

class BGO():
    def __init__(self, input: GraphHandle, gf, output: GraphHandle):
        self.name = "BGO"
        self.uuid = str(uuid.uuid4())
        self.input = input
        self.output = output
        self.gf = gf

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            gf=data["gf"],
            uuid=data["uuid"]
        )
        instance.input = GraphHandle(data["input"]["graph_data"])
        instance.output = GraphHandle(data["output"]["graph_data"])
        return instance

    def to_message(self):
        payload = {
            "name": self.name,
            "uuid": self.uuid,
            "gf": self.gf,
            "input": self.input.to_dict(),
            "output": self.output.to_dict()
        }
        return Message(self.name, payload)

    @classmethod
    def from_message(cls, message):
        return cls.from_dict(message.payload)

    def set_input(self, graph_data):
        self.input = GraphHandle(graph_data)
        print(f"{self.name} input set to: {self.input}")

    def get_output(self):
        self.output = self.input  # Dummy processing step; replace with real logic
        print(f"{self.name} output generated: {self.output}")
        return self.output
