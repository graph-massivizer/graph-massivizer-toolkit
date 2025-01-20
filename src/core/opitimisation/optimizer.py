# components/master/optimizer.py

from threading import Thread
from core.commons.terminal import Terminal
import time

class Optimizer(Thread):
    def __init__(self):
        super().__init__()
        self.name = "Optimizer"
        self.running = True
        self.terminal = Terminal.get_instance()

    def run(self):
        self.terminal.log(f"{self.name} started.", level='INFO')
        while self.running:
            # Implement optimizer logic here
            time.sleep(5)
            self.terminal.log(f"{self.name} is optimizing performance.", level='DEBUG')

    def stop(self):
        self.running = False