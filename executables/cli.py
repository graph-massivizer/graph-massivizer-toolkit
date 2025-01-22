import click

from graphmassivizer.infrastructure.simulation.lifecycle import Simulation
from graphmassivizer.runtime.task_manager import main as task_manager_main

# https://docs.google.com/drawings/d/1FC5paw_2A3nFBcIW7s99Pk1I_bSUXy_2Uma1LtBmQ_c/edit?usp=sharing


@click.group()
def main() -> None:
    """Graph-Massivizer CLI"""


@main.command()
def simulate_environment():

    import logging

    logging.basicConfig(level=logging.INFO)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    logging.getLogger("docker.utils.config").setLevel(logging.ERROR)

    simulation = Simulation(10)
    try:
        simulation.start()
        simulation.complete()
    except Exception:
        simulation.fail()
        raise


@main.group()
def tm():
    """Commands for the task manager"""


@tm.command(name="start")
def tm_start():
    task_manager_main.main()


@main.group()
def wf():
    """Commands for the workflow manager"""


@wf.command(name="start")
def wf_start():
    task_manager_main.main()


if __name__ == '__main__':
    main()
