from .base_component import BaseComponent

class User(BaseComponent):
    def __init__(self):
        super().__init__("user")

    def process_message(self, sender, message):
        print(f"{self.name} received message from {sender} on {self.name}: {message}")