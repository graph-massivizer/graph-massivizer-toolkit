from dash import Input, Output, State
from config import add_node_btn, bgo_dag_nx_graph, df_computing_nodes
import dash
import pandas as pd
from main import Dashboard

def register_callbacks(app, dashboard):
    # Callbacks for modifying the graph
    @app.callback(
        Output('cytoscape-graph', 'elements'),
        Output('output', 'children'),
        Input(add_node_btn, 'n_clicks'),
        Input('remove-node-btn', 'n_clicks'),
        Input('add-edge-btn', 'n_clicks'),
        Input('remove-edge-btn', 'n_clicks'),
        State('node-id', 'value'),
        State('source-node', 'value'),
        State('target-node', 'value'),
        State('cytoscape-graph', 'elements'),
        prevent_initial_call=True
    )
    def modify_graph(add_node, remove_node, add_edge, remove_edge, node_id, source, target, elements):
        ctx = dash.callback_context
        if not ctx.triggered:
            return elements, "No action performed."

        global bgo_dag_nx_graph
        trigger = ctx.triggered[0]['prop_id'].split('.')[0]

        # Convert elements back to NetworkX
        bgo_dag_nx_graph.clear()
        for el in elements:
            if 'source' in el['data']:  # Edges
                bgo_dag_nx_graph.add_edge(el['data']['source'], el['data']['target'])
            else:  # Nodes
                bgo_dag_nx_graph.add_node(el['data']['id'])

        # Modify Graph
        message = ""
        if trigger == 'add-node-btn' and node_id:
            if node_id not in bgo_dag_nx_graph.nodes:
                bgo_dag_nx_graph.add_node(node_id)
                message = f"Added node {node_id}"
            else:
                message = f"Node {node_id} already exists."

        elif trigger == 'remove-node-btn' and node_id:
            if node_id in bgo_dag_nx_graph.nodes:
                bgo_dag_nx_graph.remove_node(node_id)
                message = f"Removed node {node_id}"
            else:
                message = f"Node {node_id} not found."

        elif trigger == 'add-edge-btn' and source and target:
            if source in bgo_dag_nx_graph.nodes and target in bgo_dag_nx_graph.nodes:
                if not bgo_dag_nx_graph.has_edge(source, target):
                    bgo_dag_nx_graph.add_edge(source, target)
                    message = f"Added edge {source} - {target}"
                else:
                    message = f"Edge {source} - {target} already exists."
            else:
                message = "One or both nodes not found."

        elif trigger == 'remove-edge-btn' and source and target:
            if bgo_dag_nx_graph.has_edge(source, target):
                bgo_dag_nx_graph.remove_edge(source, target)
                message = f"Removed edge {source} - {target}"
            else:
                message = f"Edge {source} - {target} not found."

        return nx_to_cytoscape(bgo_dag_nx_graph), message


    # Convert NetworkX graph to Cytoscape format
    def nx_to_cytoscape(G):
        nodes = [{"data": {"id": str(n), "label": str(n)}} for n in G.nodes()]
        edges = [{"data": {"source": str(u), "target": str(v)}} for u, v in G.edges()]
        return nodes + edges
    
    @app.callback(
        Output('computing-nodes-table', 'data'),
        Output('computing-nodes-table', "columns"),
        Input("start-simulation-btn", 'n_clicks'),
        State('computing-nodes-table', 'data'),
        prevent_initial_call=True
    )
    def start_simulation(n_clicks):
        if n_clicks > 0:
            # start simulation and get computing nodes info
            

            # define computing nodes info manually
            data = {
                "address": ['localhost:/111_upd', 'localhost:/112'],
                "host_name": ['zookeeper_0', 'task_manager'],
                "hardware": ['CPU', 'GPU'],
                "cpu_cores":[512, 128],
                "ram_size":[128,  256],
                "hdd": ['1T', '2T'],
                "node_type": ['zookeeper', 'TM'] # if it is zookeper, TM or WM node
            }
            df_computing_nodes = pd.DataFrame(data=data)

            return df_computing_nodes, [{"name": col, "id": col} for col in df_computing_nodes.columns]


    @app.callback(
    Output('computing-nodes-table', 'data'),
    Input('updt-containers-btn', 'n_clicks')
    )
    def update_containers_table(n_clicks, containers_info_df):
        if n_clicks > 0:
            update_containers_info = dashboard.update_containers_info()
            return update_containers_info.to_dict('records')