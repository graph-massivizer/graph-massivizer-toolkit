# Manages data consumption for tasks.
# absorb: Retrieves data from input channels, databases, ... , handling events like source exhaustion and gate closures.
# bind: Binds input gates and allocators to the consumer.
# openGate, closeGate, isGateClosed: Methods for managing input gates.
# isExhausted: Checks if all input channels are exhausted.