# components/metafactory/metafactory.py

from threading import Thread
from commons.terminal import Terminal
import time

class Metafactory(Thread):
    def __init__(self):
        super().__init__()
        self.name = "Metafactory"
        self.running = True
        self.terminal = Terminal.get_instance()

    def run(self):
        self.terminal.log(f"{self.name} started.", level='INFO')
        while self.running:
            # Simulate database activity
            time.sleep(5)
            self.terminal.log(f"{self.name} is managing data.", level='DEBUG')

    def stop(self):
        self.running = False

def main():
    terminal = Terminal.get_instance()
    terminal.start()
    try:
        metafactory = Metafactory()
        metafactory.start()
        metafactory.join()
    except KeyboardInterrupt:
        metafactory.stop()
    finally:
        terminal.stop()

if __name__ == '__main__':
    main()