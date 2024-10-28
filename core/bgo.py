from .graph_handle import GraphHandle
from .hardware import Hardware
from .message import Message

class BGO():
    def __init__(self, input: GraphHandle, gf, hardware: Hardware, output: GraphHandle):
        self.name = "BGO"
        self.input = input
        self.output = output
        self.gf = gf
        self.hardware = hardware

    @classmethod
    def from_dict(cls, data):
        instance = cls(
            gf=data["gf"],
            hardware_type=data["hardware"]["type"],
            architecture=data["hardware"]["architecture"]
        )
        instance.input = GraphHandle(data["input"]["graph_data"])
        instance.output = GraphHandle(data["output"]["graph_data"])
        return instance

    def to_message(self):
        payload = {
            "name": self.name,
            "gf": self.gf,
            "input": self.input.to_dict(),
            "output": self.output.to_dict(),
            "hardware": self.hardware.to_dict()
        }
        return Message("BGO", payload)

    @classmethod
    def from_message(cls, message):
        return cls.from_dict(message.payload)

    def process_graph(self):
        print(f"{self.name} is processing the graph with gf={self.gf} on {self.hardware}")

    def set_input(self, graph_data):
        self.input = GraphHandle(graph_data)
        print(f"{self.name} input set to: {self.input}")

    def get_output(self):
        self.output = self.input  # Dummy processing step; replace with real logic
        print(f"{self.name} output generated: {self.output}")
        return self.output
