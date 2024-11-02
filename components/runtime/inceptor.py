# components/runtime/inceptor.py

from threading import Thread
from commons.terminal import Terminal
import time

class Inceptor(Thread):
    def __init__(self):
        super().__init__()
        self.name = "Inceptor"
        self.running = True
        self.terminal = Terminal.get_instance()

    def run(self):
        self.terminal.log(f"{self.name} started.", level='INFO')
        while self.running:
            # Implement inceptor logic here
            time.sleep(5)
            self.terminal.log(f"{self.name} is processing input data.", level='DEBUG')

    def stop(self):
        self.running = False