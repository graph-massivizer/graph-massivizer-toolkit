# Represents a single execution unit within the Task Manager.
# - start: Starts the execution unit's thread to process tasks.
# - enqueueTask: Adds a task to the execution unit's queue.
# - stop: Stops the execution unit.
# - eraseDataset: Signals the execution unit to erase a dataset.


from abc import ABC


class BGO(ABC):
    def __init__(self) -> None:
        pass

    def run(self):
        pass
