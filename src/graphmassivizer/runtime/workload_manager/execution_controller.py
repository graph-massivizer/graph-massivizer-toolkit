# Controls the execution lifecycle of a dataflow.
# - Assembles the topology using a pipeline that includes parallelization, scheduling, and deployment.
# - Manages the topology's state machine, transitioning between states like CREATED, PARALLELIZED, SCHEDULED, DEPLOYED, RUNNING, FINISHED, etc.
# - Handles iteration evaluation and coordination for iterative dataflows.

class ExecutionController:

    def __init__(self) -> None:
        pass

    def execute(self,execlutable_DAG):
        # in the first version (sequential) we jump from BGOto BGO (for loop)
        
        # we transform the zookeper
        pass