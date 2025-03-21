import os
import hashlib
from typing import List

from src.graphmassivizer.core.dataflow.data_manager import DataManager
from src.graphmassivizer.core.dataflow.graph_handle import GraphHandle


class WorkflowStep:
    def __init__(self, data_manager: DataManager, operation: BGO):
        self.data_manager = data_manager
        self.operation = operation

    def process(self, input: GraphHandle, dry_run=False) -> GraphHandle:
        """Executes the operation and determines output directory."""
        return self.operation.execute(self.data_manager, input, dry_run)

class Workflow:
    def __init__(self, steps):
        self.steps = steps

    def run(self, input: GraphHandle, dry_run=False) -> GraphHandle:
        """Runs the workflow on the input file and determines output paths."""
        current_input = input

        # TODO: is this meant to be a DAG? Adapt the looping to respect that.
        for step in self.steps:
            step_output_dir = step.process(current_input, dry_run=dry_run)
            current_input = step_output_dir  # Assume next step uses this output
        return current_input  # Final output directory
