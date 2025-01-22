from graphmassivizer.infrastructure.simulation.lifecycle import Simulation

# https://docs.google.com/drawings/d/1FC5paw_2A3nFBcIW7s99Pk1I_bSUXy_2Uma1LtBmQ_c/edit?usp=sharing


def main():

    import logging

    logging.basicConfig(level=logging.DEBUG)

    simulation = Simulation()  # Create the simulation lifecycle manager
    try:
        simulation.start()
        simulation.complete()
    except KeyboardInterrupt:
        simulation.fail()


if __name__ == '__main__':
    main()
