# components/master/parallelizer.py

from threading import Thread
from graphmassivizer.core.commons.terminal import Terminal
import time


class Parallelizer(Thread):
    def __init__(self) -> None:
        super().__init__()
        self.name = "Parallelizer"
        self.running = True
        self.terminal = Terminal.get_instance()

    def run(self) -> None:
        self.terminal.log(f"{self.name} started.", level='INFO')
        while self.running:
            # Implement optimizer logic here
            time.sleep(5)
            self.terminal.log(f"{self.name} is parallelizing.", level='DEBUG')

    def stop(self) -> None:
        self.running = False
