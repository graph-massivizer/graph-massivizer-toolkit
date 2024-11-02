# commons/terminal.py

import threading
import queue
from colorama import init, Fore, Style
import time

class Terminal:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if Terminal._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.message_queue = queue.Queue()
            self.running = False
            self.thread = threading.Thread(target=self._process_messages, daemon=True)
            init(autoreset=True)  # Initialize colorama
            Terminal._instance = self

    @staticmethod
    def get_instance():
        if Terminal._instance is None:
            with Terminal._lock:
                if Terminal._instance is None:
                    Terminal()
        return Terminal._instance

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.message_queue.put(None)  # Sentinel to unblock the queue
        self.thread.join()

    def log(self, message, level='INFO'):
        self.message_queue.put((level, message))

    def _process_messages(self):
        while True:
            item = self.message_queue.get()
            if item is None:
                break  # Exit the loop if None is received
            level, message = item
            self._output_message(level, message)
            self.message_queue.task_done()

    def _output_message(self, level, message):
        # Define colors based on level
        level_colors = {
            'DEBUG': Fore.BLUE,
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.MAGENTA
        }
        color = level_colors.get(level, Fore.WHITE)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{color}{Style.BRIGHT}[{timestamp}] [{level}] {message}{Style.RESET_ALL}")