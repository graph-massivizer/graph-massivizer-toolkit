import click
import threading
import logging
import socketserver
import pickle
import struct
import time
import os

from graphmassivizer.infrastructure.simulation.lifecycle import Simulation
from graphmassivizer.runtime.task_manager import main as task_manager_main
from graphmassivizer.runtime.workload_manager import main as workload_manager_main
from graphmassivizer.runtime.task_manager.input.preprocessing import InputPipeline
from graphmassivizer.core.descriptors.descriptors import Machine, MachineDescriptor, DeploymentDescriptor, BGODescriptor
from graphmassivizer.core.zookeeper.zookeeper_state_manager import ZookeeperStateManager

# https://docs.google.com/drawings/d/1FC5paw_2A3nFBcIW7s99Pk1I_bSUXy_2Uma1LtBmQ_c/edit?usp=sharing

# ----------------------------
# Logging Server Code
# ----------------------------
# TODO: I think this can be removed
class LogRecordStreamHandler(socketserver.StreamRequestHandler):
    """
    Receives a pickled LogRecord and reconstitutes it.
    """
    def handle(self):
        while True:
            # Read the length header (4 bytes).
            chunk = self.connection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            # Now receive the pickled LogRecord data.
            chunk = self.connection.recv(slen)
            while len(chunk) < slen:
                chunk += self.connection.recv(slen - len(chunk))
            obj = pickle.loads(chunk)
            record = logging.makeLogRecord(obj)
            logger = logging.getLogger(record.name)
            logger.handle(record)

class LogRecordSocketReceiver(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    def __init__(self, host='0.0.0.0', port=9020, handler=LogRecordStreamHandler):
        super().__init__((host, port), handler)

def run_logging_server():
    """
    Configures and runs the logging server.
    """
    # Configure the root logger to output to the console.
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s'
    )
    server = LogRecordSocketReceiver(port=9020)
    logging.getLogger(__name__).info("Logging server started on port 9020.")
    server.serve_forever()

# ----------------------------
# Existing CLI Functions
# ----------------------------

def run_simulation():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.getLogger("docker.utils.config").setLevel(logging.ERROR)
    with Simulation() as simulation:
        # simulation.wait_for_completion()
        simulation.run_default_input_pipeline()

def start_task_manager():
    task_manager_main.main()

def start_workflow_manager():
    workload_manager_main.main()

# --- Click commands ---

@click.group()
def main() -> None:
    """Graph-Massivizer CLI"""

@main.command()
def simulate_environment():
    run_simulation()

@main.group()
def tm():
    """Commands for the task manager"""

@tm.command(name="start")
def tm_start():
    start_task_manager()

@main.group()
def wf():
    """Commands for the workflow manager"""

@wf.command(name="start")
def wf_start():
    start_workflow_manager()

@main.command()
def simulate():
    try: run_simulation()
    except Exception as e: raise e

@main.command()
def interactive():
    """
    Starts an interactive command loop with the logging server running in the background.

    Available commands:
      - simulate      (to run a simulation)
      - tm start      (to start the task manager)
      - wf start      (to start the workflow manager)
      - exit or quit  (to exit interactive mode)
    """
    click.echo("Starting central logging server in background on port 9020...")
    # Start the logging server in a daemon thread
    log_thread = threading.Thread(target=run_logging_server, daemon=True)
    log_thread.start()

    click.echo("Entering interactive CLI mode. Available commands: simulate, 'tm start', 'wf start'")
    click.echo("Type 'exit' or 'quit' to leave interactive mode.\n")

    while True:
        try:
            cmd = input("Command> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nExiting interactive mode.")
            break

        if cmd in ("exit", "quit"):
            click.echo("Exiting interactive mode.")
            break
        elif cmd == "simulate":
            try: run_simulation()
            except Exception as e: raise e
        elif cmd == "tm start":
            start_task_manager()
        elif cmd == "wf start":
            start_workflow_manager()
        else:
            click.echo("Unknown command. Try 'simulate', 'tm start', 'wf start', or 'exit'.")

        # Optionally, sleep a short time to yield to background threads.
        time.sleep(0.1)

if __name__ == '__main__':
    main()
