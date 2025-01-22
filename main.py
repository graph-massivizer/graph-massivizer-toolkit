from graphmassivizer.infrastructure.simulation.lifecycle import SimulationLifecycle

# https://docs.google.com/drawings/d/1FC5paw_2A3nFBcIW7s99Pk1I_bSUXy_2Uma1LtBmQ_c/edit?usp=sharing


def main():

    import logging

    logging.basicConfig(level=logging.DEBUG)

    simulation = SimulationLifecycle()  # Create the simulation lifecycle manager

    simulation.start()
    # Transition through lifecycle stages
    # simulation.initialize_environment()
    # simulation.create_cluster(network)
    # simulation.start_simulation()
    try:
        simulation.complete()
        # while True:
        #     pass  # Keep the main thread alive
    except KeyboardInterrupt:
        print("Shutting down simulation.")
        simulation.fail()


if __name__ == '__main__':
    main()
