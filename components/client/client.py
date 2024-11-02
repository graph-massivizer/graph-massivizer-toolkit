# components/client/client.py

from threading import Thread
from commons.terminal import Terminal
import time

class Client(Thread):
    def __init__(self):
        super().__init__()
        self.name = "Client"
        self.running = True
        self.terminal = Terminal.get_instance()

    def run(self):
        self.terminal.log(f"{self.name} started.", level='INFO')
        while self.running:
            # Simulate client activity
            time.sleep(5)
            self.terminal.log(f"{self.name} is sending requests.", level='DEBUG')

    def stop(self):
        self.running = False

def main():
    terminal = Terminal.get_instance()
    terminal.start()
    try:
        client = Client()
        client.start()
        client.join()
    except KeyboardInterrupt:
        client.stop()
    finally:
        terminal.stop()

if __name__ == '__main__':
    main()