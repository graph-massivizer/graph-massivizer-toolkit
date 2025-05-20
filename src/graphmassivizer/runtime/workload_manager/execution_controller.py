# Controls the execution lifecycle of a dataflow.
# - Assembles the topology using a pipeline that includes parallelization, scheduling, and deployment.
# - Manages the topology's state machine, transitioning between states like CREATED, PARALLELIZED, SCHEDULED, DEPLOYED, RUNNING, FINISHED, etc.
# - Handles iteration evaluation and coordination for iterative dataflows.

class ExecutionController:

    def __init__(self) -> None:
        pass
    
    def execute(self) -> None:
        self.state.run()
        task = self.firstTask   
        args = self.DAG['args']
        i = 0
        while task:
            algorithm = list(task['implementations'].values())[0]['class'].run
            self.cluster.task_managers[i].run(algorithm,args)
            task = self.DAG['nodes'][list(task['next'])[0]] if task and 'next' in task else None
            i += 1