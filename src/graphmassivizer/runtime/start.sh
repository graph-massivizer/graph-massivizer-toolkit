#!/usr/bin/env bash
set -e

echo "Container started with role: ${ROLE}"

case "$ROLE" in
  "task_manager")
    echo "Starting Task Manager..."
    # Typically you run your main TaskManager code
    # For example:
    python /app/src/graphmassivizer/runtime/task_manager/main.py
    ;;
  "workflow_manager")
    echo "Starting Workload Manager..."
    # Typically you run your main Workflow Manager code
    python /app/src/graphmassivizer/runtime/workload_manager/main.py
    ;;
  *)
    echo "ERROR: Unknown or undefined ROLE."
    echo "Please set ROLE=task_manager or ROLE=workflow_manager."
    exit 1
    ;;
esac