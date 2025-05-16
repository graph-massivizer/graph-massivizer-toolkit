from graphmassivizer.core.dataflow.data_manager import DataManager
from graphmassivizer.core.dataflow.BGO import BGO

class WorkflowStep:
    def __init__(self, data_manager: DataManager, operation: BGO):
        self.data_manager = data_manager
        self.operation = operation

    def process(self, input: ObjectHandle, dry_run=False) -> ObjectHandle:
        """Executes the operation and determines output directory."""
        return self.operation.execute(self.data_manager, input, dry_run)

class Workflow:
    def __init__(self, steps):
        self.steps = steps

    def run(self, input: ObjectHandle, dry_run=False) -> ObjectHandle:
        """Runs the workflow on the input file and determines output paths."""
        current_input = input

        # TODO: is this meant to be a DAG? Adapt the looping to respect that.
        for step in self.steps:
            step_output_dir = step.process(current_input, dry_run=dry_run)
            current_input = step_output_dir  # Assume next step uses this output
        return current_input  # Final output directory
