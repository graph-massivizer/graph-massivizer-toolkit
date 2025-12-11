# Graph-Massivizer Toolkit
The Graph-Massivizer Toolkit is a loosely integrated toolkit that leverages the unique researched functionalities in each separate Graph-Massivizer tool. In the toolkit, algorithms that perform basic graph operations (BGO) developed by Graph-Inceptor and Graph-Scrutinizer as well as other open source libraries are integrated so that they can be executed efficiently and in a green-aware fashion within diverse hardware environments according to the advanced techniques developed by Graph-Optimizer, Graph-Greenifier, and Graph-Choreographer.

The architecture of the Graph-Massivizer distributed graph processing engine is designed for scalable execution across the compute continuum, including cloud, HPC and edge environments - leveraging both CPU and GPU resources. 

## Graph-Massivizer Tools

### Graph-Inceptor
The [Graph-Inceptor](https://github.com/graph-massivizer/graph-inceptor) tool is comprised of two distinct tools serving different use cases for ingesting and processing massive graphs.

- [GraphMa](https://github.com/graph-massivizer/graph-inceptor-graphma), a component of the Graph-Inceptor tool, integrates principles of pipeline computation using modular, composable functions to provide structured graph data analysis and processing using computational abstractions such as computation as type, higher-order traversal abstraction, and directed data-transfer protocol.

- The [ETL Pipeline](https://github.com/graph-massivizer/graph-inceptor-etl-pipeline) creates KGs and stores them in batches from large data sources using semantic mappings deployed on a scalable IT cloud infrastructure consisting of servers and storage systems.

### Graph-Scrutinizer
[Graph-Scrutinizer](https://github.com/graph-massivizer/graph-scrutinizer) provides various BGO analytics, such as sampling, summarisation, traversal, or ML (e.g., GNN) algorithms, translated into optimised implementations for heterogeneous hardware (HPC, edge, cloud). Examples of the Graph-Scrutinizer algorithms that can be used in BGOs include [TS2G2](https://github.com/graph-massivizer/ts2g2) and [Go Network](https://github.com/graph-massivizer/go-network).

### Graph-Optimizer
[Graph-Optimizer](https://github.com/graph-massivizer/graph-optimizer) combines analytical models, micro-benchmarking, graph sampling, simulation, and automated validation, to predict the performance and energy footprint of a given graph processing workload.

### Graph-Greenifier
[Graph-Greenifier](https://github.com/graph-massivizer/graph-greenifier) is a simulation tool for data centre operators and application developers to create scenarios that quantify the carbon impact of workloads on different locations and hardware, making informed decisions.

### Graph-Choreographer
[Graph-Choreographer](https://github.com/graph-massivizer/graph-choreographer) is a serverless orchestration tool for executing single, ensemble and batch graph applications on the computing continuum, scheduled using performance and energy tradeoffs.

# Graph-Massivizer Toolkit Simulation
For local testing and development of BGO functionalities as well as validation of use case workflows and infrastructure configurations, a simulation is provided by the project. This simulation was initially created for validation and testing purposes to ensure compatibility of the separate tool funtionalities. It follows a master--worker paradigm with two main roles: the centralized Workload Manager to coordinate opimization and scheduling, and decentralized Task Managers for executing BGOs. These components, supported by Docker-based container orchestration, monitoring services, and a ZooKeeper-based coordination layer, ensure fault-tolerance and system observability.

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
This project is built with the python programming language and uses Docker containers. Both of these must be installed to develop with the toolkit. Other packages and dependencies should be installed automatically when building and executing the simulation.

## Using metaphactory
The simulated toolkit also uses [metaphactory](https://metaphacts.com/) as a default frontend. Developers must have a key in order to pull metaphactory Docker images. A key can be obtained by filling out [this form](https://metaphacts.com/get-started#docker-trial) and mentioning the project, which will send you an email in a short time containing the key and login command.

Before running the project, use the script provided called `./start_metaphactory.sh` to run a metaphactory docker image, and then `./stop_metaphactory.sh` to close it. These images are independent of the project so they should be running in the background during different executions and not reloaded until you want to stop working with them.

## Using a custom frontend
If a user wishes to develop their own frontend, it must submit workflows in the same format as the toolkit would expect from metaphactory. An example of the required format can be found in [this](https://github.com/graph-massivizer/graph-massivizer-toolkit/blob/main/tests/resources/workflow.json) test file.

# Development
After cloning the repository, create a virtual environment to develop using this repository. It is strongly recommended to initialize a virtual environment before installing or building the simulation. For detailed instructions see [the documentation](https://docs.python.org/3/library/venv.html) for how to configure a Python virtual environment.

Once this is set up, install the dependencies using

```bash
pip install -e .
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
