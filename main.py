from graphmassivizer.infrastructure.simulation.lifecycle import Simulation

# https://docs.google.com/drawings/d/1FC5paw_2A3nFBcIW7s99Pk1I_bSUXy_2Uma1LtBmQ_c/edit?usp=sharing


def main():

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


if __name__ == '__main__':
    main()
