# Graph-Massivizer Toolkit
The Graph-Massivizer Toolkit is an integrated platform that leverages the unique researched functionalities in each separate Graph-Massivizer tool. In the integrated toolkit, algorithms that perform basic graph operations (BGO) developed by Graph-Inceptor and Graph-Scrutinizer as well as other open source libraries are integrated so that they can be executed efficiently and in a green-aware fashion within diverse hardware environments according to the advanced techniques developed by Graph-Optimizer, Graph-Greenifier, and Graph-Choreographer.

The architecture of the Graph-Massivizer distributed graph processing engine is designed for scalable execution across the compute continuum, including cloud, HPC and edge environments - leveraging both CPU and GPU resources. It follows a master--worker paradigm with two main roles: the centralized \textit{Workload Manager} to coordinate opimization and scheduling, and decentralized \textit{Task Managers} for executing BGOs. These components, supported by Docker-based container orchestration, monitoring services, and a ZooKeeper-based coordination layer, ensure fault-tolerance and system observability.

![Architecture](https://github.com/graph-massivizer/.github/figs/overview.png)

# Requirements
Developers must have a key in order to pull metaphactory Docker images. A key can be obtained by filling out [this form](https://metaphacts.com/get-started#docker-trial) and mentioning the project, which will send you an email in a short time containing the key and login command.

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
