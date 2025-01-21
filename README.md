# architecture-stubs
Architecture stubs to model different scenarios and push forward decision-making.

# Diagram
https://docs.google.com/drawings/d/1FC5paw_2A3nFBcIW7s99Pk1I_bSUXy_2Uma1LtBmQ_c/edit?usp=sharing



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
