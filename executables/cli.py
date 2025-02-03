import click
import logging
from graphmassivizer.infrastructure.simulation.lifecycle import Simulation
from graphmassivizer.runtime.task_manager import main as task_manager_main

# https://docs.google.com/drawings/d/1FC5paw_2A3nFBcIW7s99Pk1I_bSUXy_2Uma1LtBmQ_c/edit?usp=sharing

def run_simulation():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.getLogger("docker.utils.config").setLevel(logging.ERROR)
    with Simulation(10) as simulation:
        # simulation.wait_for_completion()
        print("Simulation has started, now something useful should happen.")

def start_task_manager():
    task_manager_main.main()

def start_workflow_manager():
    task_manager_main.main()

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
def interactive():
    """
    Starts an interactive command loop.
    
    Available commands:
      - simulate      (to run a simulation)
      - tm start      (to start the task manager)
      - wf start      (to start the workflow manager)
      - exit or quit  (to exit interactive mode)
    """
    print("Entering interactive CLI mode. Available commands: simulate, 'tm start', 'wf start'")
    print("Type 'exit' or 'quit' to leave interactive mode.\n")
    
    while True:
        try:
            cmd = input("Command> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting interactive mode.")
            break

        if cmd in ("exit", "quit"):
            print("Exiting interactive mode.")
            break
        elif cmd == "simulate":
            run_simulation()
        elif cmd == "tm start":
            start_task_manager()
        elif cmd == "wf start":
            start_workflow_manager()
        else:
            print("Unknown command. Try 'simulate', 'tm start', 'wf start', or 'exit'.")

if __name__ == '__main__':
    main()