# Graph-Massivizer Toolkit
The Graph-Massivizer Toolkit is an integrated platform that leverages the unique researched functionalities in each separate Graph-Massivizer tool. In the integrated toolkit, algorithms that perform basic graph operations (BGO) developed by Graph-Inceptor and Graph-Scrutinizer as well as other open source libraries are integrated so that they can be executed efficiently and in a green-aware fashion within diverse hardware environments according to the advanced techniques developed by Graph-Optimizer, Graph-Greenifier, and Graph-Choreographer.

The architecture of the Graph-Massivizer distributed graph processing engine is designed for scalable execution across the compute continuum, including cloud, HPC and edge environments - leveraging both CPU and GPU resources. It follows a master--worker paradigm with two main roles: the centralized Workload Manager to coordinate opimization and scheduling, and decentralized Task Managers for executing BGOs. These components, supported by Docker-based container orchestration, monitoring services, and a ZooKeeper-based coordination layer, ensure fault-tolerance and system observability.

![Architecture](https://github.com/graph-massivizer/.github/blob/public-update/figs/overview.png)

## Workload Manager
The Workload Manager is a centralized component running on the master node, acting as the global orchestrator of graph workflows submitted by users. Upon receiving a workflow (as a DAG), it validates its structure and decomposes it into BGOs, such as filtering, traversal, or PageRank. Its internal modules are:

- Parser and validator: ensures syntactic and semantic correctness of the user-defined graph workflow.
- Parallelizer: applies task-level parallelism to BGOs, tagging them for concurrent execution where possible.
- Hardware-aware optimizer: annotates each BGO with estimated runtime and resource metrics across multiple hardware profiles.
- Energy-aware greenifier: selects execution configurations that minimize energy usage while maintaining performance thresholds.
- Scheduler: assigns optimized tasks to Task Managers using placement strategies aware of co-location constraints, hardware affinity, and data locality.
- Deployer: publishes deployment descriptors to ZooKeeper, enabling a decoupled and event-driven execution model.
- Execution controller: oversees real-time status updates from Task Managers and adapts the schedule in case of failure or resource fluctuation.

Together, these modules turn abstract workflows into scheduled, optimized execution plans. ZooKeeper acts as the coordination bus where deployment instructions and task states are communicated asynchronously.

## Task Manager
Managers are lightweight agents deployed across the computing continuum (cloud servers, HPC nodes, edge devices). Each Task Manager executes the BGOs assigned by the Workload Manager. Their internal components are:
- Deployment watcher: monitors ZooKeeper for execution descriptors and triggers task instantiation upon availability.
- I/O interface: interacts with HDFS for reading inputs and persisting results using PyArrow's native bindings.
- Execution engine: manages one or more BGOs in parallel based on available local resources.
- Status reporter: transfers task progress, logs, and performance metrics to the Workload Manager.

Each instance of Task Manager registers itself with ZooKeeper and encodes its machine descriptor, allowing the infrastructure manager in the Workload Manager to maintain a live view of available execution resources. BGOs are designed to be stateless and containerized, enabling fault-resilient retries and elastic scaling. The Task Manager also includes demo routines for interacting with HDFS, verifying storage availability, and supporting workload validation during test cycles. The full engine supports both simulation (via lifecycle emulation in Docker) and deployment in production clusters, making it suitable for prototyping, benchmarking, and real-world graph analytics pipelines.

# Requirements
This project is built with the python programming language and uses Docker containers. Both of these must be installed to develop with the toolkit.

The platform also uses [metaphactory](https://metaphacts.com/) as a frontend. Developers must have a key in order to pull metaphactory Docker images. A key can be obtained by filling out [this form](https://metaphacts.com/get-started#docker-trial) and mentioning the project, which will send you an email in a short time containing the key and login command.

## Running metaphactory
Before running the project, use the script provided called `./start_metaphactory.sh` to run a metaphactory docker image, and then `./stop_metaphactory.sh` to close it. These images are independent of the project so they should be running in the background during different executions and not reloaded until you want to stop working with them.

# Development
After cloning the project, create a virtual environment to work on this project.
Then, install the dependencies using

```bash
pip install -e .
```

For the state machine visualizations, we make use of pydot, which in turn requires graphviz to be installed natively on you machine.
Follow instructions from https://graphviz.org/download/

After that is installed, you can install the dependencies for visualizations using:

```bash
pip install -e '.[visualization]'
```

To be able to run tests, also install test dependencies

```bash
pip install -e '.[test]'
```

Furthermore, you have to build the runtime-container. Therfore, go to the projects root and execture the script `build.sh` or run

```bash
docker build -t gm/runtime:latest .
```

When you want to run the simulation, you must build differently for Apple Silicon, which can be done by adding the `-as` flag to the build script or by running

```bash
docker buildx build --platform=linux/amd64 -t gm/runtime:latest .
```

You can try if the workload_manager / task_manager runs with

```bash
docker run --rm -e ROLE=task_manager gm/runtime:latest
docker run --rm -e ROLE=workflow_manager gm/runtime:latest
```

# Execution

Please make sure Docker runs on your system. The script `simulate.sh` is provided for quick execution of the default simulation on a local machine.

The main executable is in /exectuables/cli.py, it can be executed as

```bash
python executables/cli.py
```

It has options to run the graph massivizer in a local simulation and to start workflow and task managers.
Run
```bash
python executables/cli.py --help
```
for more information.

For interactive mode run
Run
```bash
python executables/cli.py interactive
```

To directly run the simulation try
Run
```bash
python executables/cli.py simulate
```
