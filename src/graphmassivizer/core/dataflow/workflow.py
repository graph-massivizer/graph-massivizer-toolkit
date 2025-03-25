import os
import hashlib


class WorkflowStep:
    def __init__(self, name, operation):
        """A step in the workflow.

        :param name: Name of the step (unique).
        :param operation: A callable function that processes the input.
        """
        self.name = name
        self.operation = operation

    def process(self, input_file, output_dir):
        """Executes the operation and determines output directory."""
        step_hash = hashlib.md5(self.name.encode()).hexdigest()[:8]
        step_output_dir = os.path.join(output_dir, f"{self.name}_{step_hash}")
        os.makedirs(step_output_dir, exist_ok=True)
        return step_output_dir


class Workflow:
    def __init__(self, steps, base_output_dir):
        """Initializes the workflow with a sequence of steps.

        :param steps: List of WorkflowStep objects.
        :param base_output_dir: Root output directory.
        """
        self.steps = steps
        self.base_output_dir = base_output_dir

    def run(self, input_file):
        """Runs the workflow on the input file and determines output paths."""
        current_input = input_file
        current_output_dir = self.base_output_dir
        for step in self.steps:
            step_output_dir = step.process(current_input, current_output_dir)
            current_input = step_output_dir  # Assume next step uses this output
            current_output_dir = step_output_dir  # Update output location
        return current_output_dir  # Final output directory
