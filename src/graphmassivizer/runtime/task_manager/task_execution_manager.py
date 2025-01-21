# Manages the execution units within the Task Manager.
# scheduleTask: Schedules a task on an execution unit based on load balancing.
# getExecutionUnitByTaskID: Retrieves the execution unit responsible for a specific task.
# The TaskExecutionManager is responsible for:

# 	•	Managing multiple TaskExecutionUnit instances.
# 	•	Scheduling tasks to execution units based on their load.
# 	•	Providing methods to retrieve execution units by task ID.


import threading
import logging
import uuid
import time
from typing import List, Optional


class TaskExecutionManager:
    def __init__(self, task_manager, machine_descriptor, buffer_memory_manager, number_of_execution_units) -> None:
        if task_manager is None:
            raise ValueError("task_manager cannot be None")
        if machine_descriptor is None:
            raise ValueError("machine_descriptor cannot be None")
        if buffer_memory_manager is None:
            raise ValueError("buffer_memory_manager cannot be None")
        if number_of_execution_units < 1:
            raise ValueError("number_of_execution_units must be at least 1")

        self.task_manager = task_manager
        self.machine_descriptor = machine_descriptor
        self.buffer_memory_manager = buffer_memory_manager
        self.number_of_execution_units = number_of_execution_units
        self.execution_units: List[TaskExecutionUnit] = []

        self.logger = logging.getLogger(self.__class__.__name__)
        self.initialize_execution_units()

    def initialize_execution_units(self) -> None:
        for i in range(self.number_of_execution_units):
            input_buffer = self.buffer_memory_manager.get_buffer_allocator_group()
            output_buffer = self.buffer_memory_manager.get_buffer_allocator_group()
            execution_unit = TaskExecutionUnit(self, i, input_buffer, output_buffer)
            execution_unit.start()
            self.execution_units.append(execution_unit)
            self.logger.debug(f"Initialized execution unit {i}")

    def schedule_task(self, runtime: TaskRuntime) -> None:
        if runtime is None:
            raise ValueError("runtime cannot be None")

        # Find execution unit with the fewest enqueued tasks
        with threading.Lock():
            selected_eu = min(self.execution_units, key=lambda eu: eu.get_number_of_enqueued_tasks())

        selected_eu.enqueue_task(runtime)

        # Build log message
        sb = ""
        invokeable = runtime.get_invokeable()
        node_descriptor = runtime.get_node_descriptor()
        if invokeable is not None:
            if isinstance(invokeable, DatasetDriver2):
                sb = f"Dataset NAME:{node_descriptor.name} TASK ID: {node_descriptor.task_id}"
            elif isinstance(invokeable, OperatorDriver):
                sb = f"Operator NAME:{node_descriptor.name} TASK ID: {node_descriptor.task_id}"
            elif isinstance(invokeable, AbstractInvokeable):
                sb = "Invokeable"
            else:
                sb = f"NAME:{node_descriptor.name} TASK ID: {node_descriptor.task_id}"
        else:
            sb = "Empty"

        self.logger.info(
            f"EXECUTE TASK {node_descriptor.name}-{node_descriptor.task_index} [{node_descriptor.task_id}] "
            f"ON EXECUTION UNIT ({selected_eu.get_execution_unit_id()}) ON MACHINE [{self.machine_descriptor.uid}] "
            f"-- QUEUE LENGTH: {selected_eu.get_number_of_enqueued_tasks()} -- CURRENTLY RUNNING {sb}"
        )

    def get_execution_unit_by_task_id(self, task_id: uuid.UUID) -> Optional[TaskExecutionUnit]:
        if task_id is None:
            raise ValueError("task_id cannot be None")

        execution_unit_for_task = self.find_execution_unit_by_task_id(task_id)

        # Retry logic as in Java code
        retry_count = 20
        for _ in range(retry_count):
            if execution_unit_for_task is not None:
                break
            time.sleep(0.05)  # Sleep 50 milliseconds
            execution_unit_for_task = self.find_execution_unit_by_task_id(task_id)

        if execution_unit_for_task is None:
            self.logger.warning(f"Could not find execution unit for task ID {task_id}")
            return None

        return execution_unit_for_task

    def find_execution_unit_by_task_id(self, task_id: uuid.UUID) -> Optional[TaskExecutionUnit]:
        for eu in self.execution_units:
            runtime = eu.get_runtime()
            if runtime is not None and runtime.get_node_descriptor().task_id == task_id:
                return eu
        return None

    def get_task_manager(self):
        return self.task_manager

    def get_execution_units(self) -> List[TaskExecutionUnit]:
        return self.execution_units

    def stop_all_execution_units(self) -> None:
        for eu in self.execution_units:
            eu.stop()
        for eu in self.execution_units:
            eu.join()
        self.logger.info("All execution units have been stopped.")
