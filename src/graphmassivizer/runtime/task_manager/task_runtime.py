# Manages the runtime environment for a single task.
# - initialize: Initializes the task by setting up the consumer, producer, and invokable (the actual task logic).
# - execute: Executes the task by calling the invokable's create, open, run, and close methods.
# - release: Releases resources associated with the task.
# - connectDataChannel: Establishes a data channel to another task.
# - getNextInputSplit: Retrieves the next input split for HDFS sources.
# - shutdownRuntime: Shuts down the task runtime.


from graphmassivizer.runtime.task_manager.task_execution_unit import BGO


class BGOMapper:
    """Maps BGO identifier to implementation"""

    bgos = {
        "betweenness_centrality":

    }

    def select(self, id: str) -> BGO:
