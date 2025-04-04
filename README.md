# architecture-stubs
Architecture stubs to model different scenarios and push forward decision-making.

# Diagram
https://docs.google.com/drawings/d/1FC5paw_2A3nFBcIW7s99Pk1I_bSUXy_2Uma1LtBmQ_c/edit?usp=sharing

# Requirements
Developers must have a key in order to pull metaphactory Docker images. A key can be obtained for free by filling out this form and mentioning the GM project, which will send you an email in a short time containing the key and login command.

https://metaphacts.com/get-started#docker-trial

## Running metaphactory

Before running the project, use the script provided called `./start_metaphactory.sh` to run a metaphactory docker image, and then `./stop_metaphactory.sh` to close it. These images are independent of the project so they should be running in the background during different executions and not reloaded until you want to stop working with them.

# Getting started with coding

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

Furthermore, you have to build the runtime-container. Therfore, go to the projects root and run

```bash
docker build -t gm/runtime:latest .
```

When you want to run the simulation, you must build differently for Apple Silicon

```bash
docker buildx build --platform=linux/amd64 -t gm/runtime:latest .
```

You can try if the workload_manager / task_manager runs with

```bash
docker run --rm -e ROLE=task_manager gm/runtime:latest
docker run --rm -e ROLE=workflow_manager gm/runtime:latest
```

# executing

Please make sure Docker runs on your system.

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
