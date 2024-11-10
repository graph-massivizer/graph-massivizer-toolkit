# Manages data production for tasks.
# - emit: Sends data to output channels, handling both data events and buffers.
# - broadcast: Broadcasts data to all connected tasks.
# - done: Signals that the producer has finished sending data on a specific gate.
# - shutdown: Shuts down the producer and closes output channels.
# - bind: Binds output gates and allocators to the producer.