from graphmassivizer.infrastructure.simulation.node import Node, ZookeeperNode


class Cluster:

    docker_network_name = 'cluster_net'

    def __init__(self, zookeeper: ZookeeperNode, workflow_manager: WorkflowManagerNode, task_managers: list[TaskMaangerNode]) -> None:
        self.zookeeper = zookeeper
        self.workload_manager = workflow_manager
        self.task_managers = task_managers

    # def monitor_cluster(self) -> None:
    #     for node in self.nodes.values():
    #         status = node.report_status()
    #         print(
    #             f"Node {status['node_id']}: Status {status['status']}, Task Queue Length {status['task_queue_length']}")

    # def receive_message(self, message: str) -> None:
    #     raise NotImplementedError()
