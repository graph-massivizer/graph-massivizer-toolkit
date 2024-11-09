from simulation.network import Network
from simulation.lifecycle import SimulationLifecycle
from simulation.cluster import Cluster

def main():
    network = Network()  # Initialize the network
    simulation = SimulationLifecycle()  # Initialize the simulation lifecycle manager
    
    # Transition through lifecycle stages
    simulation.initialize_environment()
    simulation.create_cluster(network)
    simulation.start_simulation()
    simulation.complete()

if __name__ == '__main__':
    main()