

import logging
import random
from collections import deque

# Now, define the Scheduler class
from collections import deque


class Scheduler:
    def __init__(self, infrastructure_manager: InfrastructureManager) -> None:
        if infrastructure_manager is None:
            raise ValueError("infrastructure_manager cannot be None")
        self.infrastructure_manager = infrastructure_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        # Dispatcher or event system can be implemented as needed
        self.dispatcher = StateMachine()

    def apply(self, topology: AuraTopology) -> AuraTopology:
        self.schedule_topology(topology)
        # Dispatch the state transition event
        event = StateMachine.FSMTransitionEvent(TopologyTransition.TOPOLOGY_TRANSITION_SCHEDULE)
        # Assuming the dispatcher has a method to handle events
        # self.dispatcher.dispatch_event(event)
        return topology

    def schedule_topology(self, topology: AuraTopology) -> None:
        self.logger.debug(
            f"Schedule topology [{topology.name}] on {self.infrastructure_manager.get_number_of_machines()} task managers"
        )

        nodes_required_to_co_locate_to = []
        nodes_with_co_location_requirements = []
        nodes_with_preferred_locations = []

        for node in topology.nodes_from_source_to_sink():
            if node.has_co_location_requirements():
                nodes_with_co_location_requirements.append(node)
                task_to_co_locate_to_name = node.properties_list[0].get('co_location_task_name')
                nodes_required_to_co_locate_to.append(topology.node_map.get(task_to_co_locate_to_name))
            elif node.is_hdfs_source():
                nodes_with_preferred_locations.append(node)

        # Schedule nodes required by others first
        self.schedule_collection_of_elements(nodes_required_to_co_locate_to, topology)
        self.schedule_collection_of_elements(nodes_with_co_location_requirements, topology)

        # Schedule nodes that prefer locations
        self.schedule_collection_of_elements(nodes_with_preferred_locations, topology)

        # Schedule all remaining nodes
        remaining_nodes = [node for node in topology.nodes_from_source_to_sink()
                           if node not in nodes_required_to_co_locate_to
                           and node not in nodes_with_co_location_requirements
                           and node not in nodes_with_preferred_locations]
        self.schedule_collection_of_elements(remaining_nodes, topology)

    def schedule_collection_of_elements(self, nodes: List[LogicalNode], topology: AuraTopology) -> None:
        for node in nodes:
            self.schedule_element(node, topology)

    def schedule_element(self, element: LogicalNode, topology: AuraTopology) -> None:
        location_preferences = self.compute_location_preferences(element, topology)

        for en in element.get_execution_nodes():
            if not en.logical_node.is_already_deployed:
                if location_preferences and location_preferences:
                    machine = self.infrastructure_manager.get_machine(location_preferences.popleft())
                else:
                    machine = self.infrastructure_manager.get_machine()

                en.get_node_descriptor().set_machine_descriptor(machine)
            self.logger.debug(
                f"{en.get_node_descriptor().machine_descriptor.address} -> "
                f"{en.get_node_descriptor().name}_{en.get_node_descriptor().task_index}"
            )

    def compute_location_preferences(self, element: LogicalNode, topology: AuraTopology) -> deque:
        location_preferences = deque()

        if element.has_co_location_requirements():
            task_to_co_locate_to_name = element.properties_list[0].get('co_location_task_name')
            task_to_co_locate_to = topology.node_map.get(task_to_co_locate_to_name)

            if task_to_co_locate_to is None:
                raise Exception("Task to co-locate to not found.")

            if not task_to_co_locate_to.is_already_deployed:
                raise Exception("Task to co-locate to not yet deployed.")

            for execution_node in task_to_co_locate_to.get_execution_nodes():
                machine = execution_node.get_node_descriptor().machine_descriptor
                location_preferences.append(LocationPreference(machine, LocationPreference.PreferenceLevel.REQUIRED))

        elif element.is_hdfs_source():
            input_splits = self.infrastructure_manager.register_hdfs_source(element)

            # Shuffle input splits to assign them evenly to hosts
            random.shuffle(input_splits)

            for input_split in input_splits:
                machines = self.infrastructure_manager.get_machines_with_input_split(input_split)
                location_preferences.append(LocationPreference(machines, LocationPreference.PreferenceLevel.PREFERRED))

        return location_preferences