from simulation.network import Network
from simulation.lifecycle import SimulationLifecycle
from simulation.cluster import Cluster

#https://docs.google.com/drawings/d/1FC5paw_2A3nFBcIW7s99Pk1I_bSUXy_2Uma1LtBmQ_c/edit?usp=sharing

def main():
    network = Network()  # Initialize the network
    simulation = SimulationLifecycle()  # Initialize the simulation lifecycle manager
    
    # Transition through lifecycle stages
    simulation.initialize_environment()
    simulation.create_cluster(network)
    simulation.start_simulation()
    simulation.complete()
    try:
        while True:
            pass  # Keep the main thread alive
    except KeyboardInterrupt:
        print("Shutting down simulation.")
        simulation.complete()

if __name__ == '__main__':
    main()