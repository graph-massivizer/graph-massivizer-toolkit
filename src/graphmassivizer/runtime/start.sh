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
  "dashboard")
    echo "Starting Dashboard..."
    # Typically you run your main Dashboard code
    python /app/src/graphmassivizer/runtime/dashboard/main.py
    ;;
  *)
    echo "ERROR: Unknown or undefined ROLE."
    echo "Please set ROLE=task_manager, ROLE=workflow_manager or ROLE=dashboard."
    exit 1
    ;;
esac
