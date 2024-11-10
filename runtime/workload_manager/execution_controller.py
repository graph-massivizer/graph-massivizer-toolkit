# Controls the execution lifecycle of a dataflow.
# - Assembles the topology using a pipeline that includes parallelization, scheduling, and deployment.
# - Manages the topology's state machine, transitioning between states like CREATED, PARALLELIZED, SCHEDULED, DEPLOYED, RUNNING, FINISHED, etc.
# - Handles iteration evaluation and coordination for iterative dataflows.