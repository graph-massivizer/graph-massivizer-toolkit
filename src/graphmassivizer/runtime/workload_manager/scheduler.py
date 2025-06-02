# import logging
# import random

# # Now, define the Scheduler class
# from collections import deque

# # INPUT INFRASTRUCTURE MANAGER: to get all Machine Descriptors for the task managers
# # INPUT optimized and greenified DAG coming from greenifier step in the WM:
# # OUTPUT Scheduled DAG with all the nodes having a machine descriptor assigned to them 
# # (the nodes of the DAG are the Deployment Descriptors)
# class Scheduler:
import logging
import random # Added import for random
import json   # Added import for json

# Assuming MachineDescriptor is in this path based on your project structure
from graphmassivizer.core.descriptors.descriptors import MachineDescriptor
# Assuming ZookeeperStateManager might be needed for type hinting or specific exceptions
from graphmassivizer.core.zookeeper.zookeeper_state_manager import ZookeeperStateManager
# For Kazoo specific exceptions like NoNodeError
from kazoo.exceptions import NoNodeError
from graphmassivizer.core.descriptors.descriptors import DeploymentDescriptor


logging.basicConfig(level=logging.INFO)

TASK_MANAGERS_ZK_PATH = "/taskmanagers"

class Scheduler:
    def __init__(self, workload_manager) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.workload_manager = workload_manager
        # self.zk should be an instance of ZookeeperStateManager
        self.zk: ZookeeperStateManager = workload_manager.zk

    @staticmethod # Marking as staticmethod as it doesn't use self and is called via Scheduler.algorithmsInDAG
    def algorithmsInDAG(DAG):
        """
        Helper function to extract algorithm implementations from a DAG.
        Note: This was present in your snippet. If called via an instance (self.algorithmsInDAG),
        it would need 'self' as the first argument. Called via class (Scheduler.algorithmsInDAG),
        @staticmethod is appropriate or it works as a class-scoped function.
        """
        return {y:z for x in DAG['nodes'].values() for y,z in x['implementations'].items()}

    def get_random_taskmanager(self) -> MachineDescriptor | None:
        """
        Fetches all registered Task Managers from ZooKeeper,
        and returns a MachineDescriptor of a randomly selected one.
        Returns None if no Task Managers are found or an error occurs.
        """
        self.logger.info(f"Attempting to get a random task manager from ZooKeeper path: {TASK_MANAGERS_ZK_PATH}")
        try:
            task_manager_ids = self.zk.get_children(TASK_MANAGERS_ZK_PATH)
        except NoNodeError:
            self.logger.warning(f"ZooKeeper path {TASK_MANAGERS_ZK_PATH} does not exist. No task managers to select.")
            return None
        except Exception as e:
            self.logger.error(f"Error fetching task manager IDs from ZooKeeper: {e}")
            return None

        if not task_manager_ids:
            self.logger.warning("No task managers registered in ZooKeeper.")
            return None

        self.logger.info(f"Found task manager IDs: {task_manager_ids}")
        
        available_descriptors: list[MachineDescriptor] = []
        for tm_id in task_manager_ids:
            node_path = f"{TASK_MANAGERS_ZK_PATH}/{tm_id}"
            try:
                data_bytes, stat = self.zk.get(node_path)
                if data_bytes:
                    machine_data_dict = json.loads(data_bytes.decode('utf-8'))
                    
                    # The data stored is from Machine.to_dict(), which contains a 'descriptor' field
                    descriptor_dict = machine_data_dict.get('descriptor')
                    
                    if not descriptor_dict:
                        self.logger.warning(f"No 'descriptor' field found in data for Task Manager {tm_id} at {node_path}. Skipping.")
                        continue

                    # Create a MachineDescriptor instance
                    # Values like cpu_cores, ram_size, hdd are stored as strings by MachineDescriptor.to_dict(),
                    # so they need to be converted back to int.
                    md = MachineDescriptor(
                        address=descriptor_dict['address'],
                        host_name=descriptor_dict['host_name'],
                        hardware=descriptor_dict['hardware'],
                        cpu_cores=int(descriptor_dict['cpu_cores']),
                        ram_size=int(descriptor_dict['ram_size']),
                        hdd=int(descriptor_dict['hdd'])
                    )
                    # Assign the ZookeeperStateManager instance from the WorkloadManager.
                    # This is important if this MachineDescriptor is used to create
                    # other Descriptors (like DeploymentDescriptor) that expect
                    # a consistent zk_state_manager.
                    # This bypasses the Descriptor.__init__ registration, which is correct
                    # as these TMs are already registered.
                    md.zk_state_manager = self.zk 
                    available_descriptors.append(md)
                    self.logger.debug(f"Successfully parsed descriptor for Task Manager {tm_id}: {md}")

                else:
                    self.logger.warning(f"No data found for Task Manager {tm_id} at {node_path}. Skipping.")
            except NoNodeError:
                self.logger.warning(f"Task Manager node {node_path} was removed after listing. Skipping.")
            except json.JSONDecodeError:
                self.logger.error(f"Failed to decode JSON for Task Manager {tm_id} at {node_path}. Data: {data_bytes[:100]}...") # Log snippet of data
            except KeyError as e:
                self.logger.error(f"Missing expected key {e} in data for Task Manager {tm_id} at {node_path}.")
            except ValueError as e: # Handles int conversion errors
                self.logger.error(f"Error converting string to int for Task Manager {tm_id} descriptor fields: {e}")
            except Exception as e:
                self.logger.error(f"An unexpected error occurred while processing Task Manager {tm_id} at {node_path}: {e}")

        if not available_descriptors:
            self.logger.warning("Could not retrieve any valid machine descriptors for task managers.")
            return None

        selected_descriptor = random.choice(available_descriptors)
        self.logger.info(f"Randomly selected task manager descriptor: {selected_descriptor.host_name} (ID part of path: {selected_descriptor.get_id() if hasattr(selected_descriptor, 'get_id') else 'N/A'})") # get_id might not be relevant here if we just need the descriptor attributes
        return selected_descriptor
    
    def schedule(self, DAG):
        self.logger.info(f"WE ARE COOKING....")
        bgoDes = Scheduler.algorithmsInDAG(DAG)
        self.logger.info(f"GOT BGO DESCRIPTORS: {bgoDes}")
        maDesc = self.get_random_taskmanager()
        self.logger.info(f"GOT MACHINE DESCRIPTOR: {maDesc}")
        deplDesc = DeploymentDescriptor(
            bgo_descriptors=bgoDes,
            machine_descriptor=maDesc,
            zk_state_manager=self.zk
        )
        self.logger.info(f"GOT DEPLOYMENT DESCRIPTOR: {deplDesc}")
        
        
        
        
        # deployment_descriptors = 
        
        