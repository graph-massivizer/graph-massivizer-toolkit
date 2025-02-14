
import networkx as nx


def run():
    input_path = "graph.txt"
    input = nx.read_edgelist(input_path)
    bfs_graph = nx.bfs_tree(input, source="0", depth_limit=2)
    betweenness = nx.betweenness_centrality(bfs_graph)
    def f(k_v): return k_v[1]
    max_betweenness = max(betweenness.items(), key=f)

    print(max_betweenness)


run()
