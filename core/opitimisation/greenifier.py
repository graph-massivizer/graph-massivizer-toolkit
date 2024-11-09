# components/master/greenifier.py

from threading import Thread
from core.commons.terminal import Terminal
import time

class Greenifier(Thread):
    def __init__(self):
        super().__init__()
        self.name = "Greenifier"
        self.running = True
        self.terminal = Terminal.get_instance()

    def run(self):
        self.terminal.log(f"{self.name} started.", level='INFO')
        while self.running:
            # Implement greenifier logic here
            time.sleep(5)
            self.terminal.log(f"{self.name} is optimizing energy usage.", level='DEBUG')

    def stop(self):
        self.running = False