import networkx as nx
import pandas as pd

# ids
add_node_btn = 'add-node-btn'

# BGO DAG nx graph
bgo_dag_nx_graph = nx.DiGraph()
edges = [("Load graph", "Extract subgraph"), ("Load graph", "Extract features"), ("Extract features", "Enhance graph"), ("Extract subgraph", "Enhance graph"), ('Enhance graph', 'Calc Pagerank centrality'), ('Calc Pagerank centrality', 'Calc scores')]
bgo_dag_nx_graph.add_edges_from(edges)

# initial computing nodes dataframe
# sample data
data = {
    "address": ['localhost:/111', 'localhost:/112'],
    "host_name": ['zookeeper_0', 'task_manager'],
    "hardware": ['CPU', 'GPU'],
    "cpu_cores":[256, 128],
    "ram_size":[128,  256],
    "hdd": ['1T', '2T'],
    "node_type": ['zookeeper', 'TM'] # if it is zookeper, TM or WM node
}
df_computing_nodes = pd.DataFrame(data=data)

dashboard_obj = None

times = []
cpu_usages = {}
mem_usages = {}