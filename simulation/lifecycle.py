from enum import Enum
from simulation.cluster import Cluster
from simulation.node import Node

class LifecycleState(Enum):
    INITIALIZED = 'INITIALIZED'
    ENVIRONMENT_SETUP = 'ENVIRONMENT_SETUP'
    CLUSTER_CREATED = 'CLUSTER_CREATED'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'

class SimulationLifecycle:
    def __init__(self):
        self.state = LifecycleState.INITIALIZED

    def transition(self, new_state):
        if new_state not in LifecycleState:
            raise ValueError(f"Invalid state: {new_state}")
        self.state = new_state
        print(f"State transitioned to: {self.state}")

    def initialize_environment(self):
        if self.state == LifecycleState.INITIALIZED:
            print("Initializing environment...")
            # Initialize the environment and deploy Zookeeper
            self.transition(LifecycleState.ENVIRONMENT_SETUP)
        else:
            print("Cannot initialize environment from current state.")
    
    # TODO: zookeeper deployment should probably be moved to a seperate deplyment phase
    def create_cluster(self, network):
        if self.state == LifecycleState.ENVIRONMENT_SETUP:
            print("Creating cluster with 10 nodes...")
            cluster = Cluster(network)
            self.cluster = cluster
            for i in range(10):
                node = Node(node_id=f"node-{i}", resources={}, network=network)
                cluster.add_node(node)
            # Deploy Zookeeper on one of the nodes
            cluster.nodes["node-0"].deploy_zookeeper()
            self.transition(LifecycleState.CLUSTER_CREATED)
        else:
            print("Cannot create cluster from current state.")
            
    # TODO: workload_manager deployment should probably be moved to a seperate deplyment phase 
    def start_simulation(self):
        if self.state == LifecycleState.CLUSTER_CREATED:
            print("Starting workload manager on node-1...")
            cluster = self.cluster  # Use the stored cluster reference
            cluster.nodes["node-1"].deploy_workload_manager()
            print("Simulation is running...")
            self.transition(LifecycleState.RUNNING)
        else:
            print("Cannot start simulation from current state.")
    
    def complete(self):
        if self.state == LifecycleState.RUNNING:
            print("Simulation completed.")
            self.transition(LifecycleState.COMPLETED)
        else:
            print("Cannot complete simulation from current state.")

    def fail(self):
        print("Simulation failed.")
        self.transition(LifecycleState.FAILED)