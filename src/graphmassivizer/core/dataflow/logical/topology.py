from enum import Enum


class TopologyState(Enum):
    CREATED = 'TOPOLOGY_STATE_CREATED'
    PARALLELIZED = 'TOPOLOGY_STATE_PARALLELIZED'
    SCHEDULED = 'TOPOLOGY_STATE_SCHEDULED'
    DEPLOYED = 'TOPOLOGY_STATE_DEPLOYED'
    RUNNING = 'TOPOLOGY_STATE_RUNNING'
    FINISHED = 'TOPOLOGY_STATE_FINISHED'
    CANCELED = 'TOPOLOGY_STATE_CANCELED'
    FAILURE = 'TOPOLOGY_STATE_FAILURE'
    ERROR = 'ERROR'


class TopologyTransition(Enum):
    PARALLELIZE = 'TOPOLOGY_TRANSITION_PARALLELIZE'
    SCHEDULE = 'TOPOLOGY_TRANSITION_SCHEDULE'
    DEPLOY = 'TOPOLOGY_TRANSITION_DEPLOY'
    RUN = 'TOPOLOGY_TRANSITION_RUN'
    NEXT_ITERATION = 'TOPOLOGY_TRANSITION_NEXT_ITERATION'
    FINISH = 'TOPOLOGY_TRANSITION_FINISH'
    CANCEL = 'TOPOLOGY_TRANSITION_CANCEL'
    FAIL = 'TOPOLOGY_TRANSITION_FAIL'


class Topology:
    def __init__(self, name: str, machine_id: str) -> None:
        self.name = name
        self.machine_id = machine_id
        self.state = TopologyState.CREATED
        self.nodes = []
        self.edges = []

    def add_node(self, node) -> None:
        self.nodes.append(node)

    def add_edge(self, src, dst) -> None:
        self.edges.append((src, dst))

    def transition_state(self, transition) -> None:
        if transition == TopologyTransition.PARALLELIZE:
            self.state = TopologyState.PARALLELIZED
        elif transition == TopologyTransition.SCHEDULE:
            self.state = TopologyState.SCHEDULED
        elif transition == TopologyTransition.DEPLOY:
            self.state = TopologyState.DEPLOYED
        elif transition == TopologyTransition.RUN:
            self.state = TopologyState.RUNNING
        elif transition == TopologyTransition.FINISH:
            self.state = TopologyState.FINISHED
        elif transition == TopologyTransition.CANCEL:
            self.state = TopologyState.CANCELED
        elif transition == TopologyTransition.FAIL:
            self.state = TopologyState.FAILURE
        else:
            self.state = TopologyState.ERROR

    def __repr__(self) -> str:
        return f"Topology(name={self.name}, state={self.state}, nodes={len(self.nodes)}, edges={len(self.edges)})"
