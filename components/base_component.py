from queue import Queue
import threading
import time

class BaseComponent:
    topics = {}

    def __init__(self, name):
        self.name = name
        self.local_queue = Queue()

    def emit_message(self, message, topic):
        print(BaseComponent.topics.keys())
        if topic == "*":
            topics = [x for x in BaseComponent.topics.keys() if x.endswith("_*")]
        else:
            topics = [topic]
        for t in topics: 
            if t not in BaseComponent.topics:
                BaseComponent.topics[t] = Queue()
            BaseComponent.topics[t].put((self.name, message.to_json()))
            print(f"{self.name} emitted message to {t}: {message.to_json()}")

    def start_listening(self):
        if self.name not in BaseComponent.topics:
            BaseComponent.topics[self.name] = Queue()
            BaseComponent.topics["{}_*".format(self.name)] = Queue()

        def listen():
            while True:
                sender, message = BaseComponent.topics[self.name].get()
                self.process_message(sender, message)
                BaseComponent.topics[self.name].task_done()


        def listen_wildcard():
            while True:
                sender, message = BaseComponent.topics["{}_*".format(self.name)].get()
                self.process_message(sender, message)
                BaseComponent.topics["{}_*".format(self.name)].task_done()

        
        listener_thread = threading.Thread(target=listen, daemon=True)
        listener_thread.start()
        print(f"{self.name} is listening on topic '{self.name}'")
        listener_thread_wildcard = threading.Thread(target=listen_wildcard, daemon=True)
        listener_thread_wildcard.start()

    def process_message(self, sender, message):
        print(f"{self.name} received message from {sender} on {self.name}: {message}")
