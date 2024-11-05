# components/master/main.py

from threading import Thread
from flask import Flask, request, jsonify, render_template
from commons.terminal import Terminal
import time
import json
import os
import igraph as ig
from flask_cors import CORS  # Added for CORS handling

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Terminal singleton instance
terminal = Terminal.get_instance()

# Path to stored graphs
GRAPH_STORAGE_DIR = 'stored_graphs'
os.makedirs(GRAPH_STORAGE_DIR, exist_ok=True)

from management.lifecycle_manager import LifecycleManager

lifecycle_manager = LifecycleManager()

# Existing API routes
@app.route('/')
def home():
    return "Master Component API is running."

@app.route('/api/submit_dag', methods=['POST'])
def submit_dag():
    """
    Receive DAG data from client, convert it to igraph format, and store it.
    """
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided.'}), 400
    
    if 'nodes' not in data or 'edges' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid data format.'}), 400
    
    nodes = data['nodes']
    edges = data['edges']
    
    try:
        # Convert to igraph
        graph = convert_to_igraph(nodes, edges)
        
        # Assign a unique identifier for the graph (e.g., timestamp)
        graph_id = f"graph_{int(time.time())}"
        graph_filename = os.path.join(GRAPH_STORAGE_DIR, f"{graph_id}.graphml")
        
        # Save graph to GraphML (supports arbitrary attributes)
        graph.write_graphml(graph_filename)
        
        terminal.log(f"DAG received and stored as {graph_filename}.", level='INFO')
        
        return jsonify({'status': 'success', 'message': f'DAG stored as {graph_filename}', 'graph_id': graph_id}), 200
    except Exception as e:
        terminal.log(f"Error processing DAG: {e}", level='ERROR')
        return jsonify({'status': 'error', 'message': str(e)}), 500

def convert_to_igraph(nodes, edges):
    """
    Converts the DAG JSON data into an igraph Graph object.
    Supports arbitrary attributes by assigning all key-value pairs in nodes and edges.
    
    Parameters:
        nodes (list): List of node dictionaries.
        edges (list): List of edge dictionaries.
    
    Returns:
        ig.Graph: The constructed igraph Graph object.
    """
    # Create a mapping from node id to index
    node_ids = [node['id'] for node in nodes]
    id_to_index = {node_id: idx for idx, node_id in enumerate(node_ids)}
    
    # Initialize the graph
    g = ig.Graph(directed=True)
    g.add_vertices(len(nodes))
    
    # Add node attributes
    for idx, node in enumerate(nodes):
        # Assign all key-value pairs as attributes except 'id'
        for key, value in node.items():
            if key != 'id':
                g.vs[idx][key] = value
        g.vs[idx]['name'] = node['id']  # 'name' is a special attribute in igraph
    
    # Add edges
    edge_tuples = [(id_to_index[edge['source']], id_to_index[edge['target']]) for edge in edges]
    g.add_edges(edge_tuples)
    
    # Add edge attributes if any
    for idx, edge in enumerate(edges):
        for key, value in edge.items():
            if key not in ['source', 'target']:
                g.es[idx][key] = value
    
    return g

# New Web Interface Routes
@app.route('/web')
def web_interface():
    """
    Render the web interface for DAG manipulation.
    """
    # Load DAG from file
    dag_file = os.path.join(os.getcwd(), 'dag.json')
    if os.path.exists(dag_file):
        with open(dag_file, 'r') as f:
            dag = json.load(f)
        terminal.log("Loaded existing DAG from dag.json.", level='INFO')
    else:
        # Initialize with predefined DAG if not present
        dag = {
            'nodes': [
                {'id': 'LoadGraphX', 'category': 'load'},
                {'id': 'Partition', 'category': 'process'},
                {'id': 'CountEdges1', 'category': 'process'},
                {'id': 'CountEdges2', 'category': 'process'},
                {'id': 'CountEdges3', 'category': 'process'},
                {'id': 'PageRank', 'category': 'process'},
                {'id': 'ShortestPath', 'category': 'process'},
                {'id': 'StoreResult', 'category': 'store'}
            ],
            'edges': [
                {'source': 'LoadGraphX', 'target': 'Partition'},
                {'source': 'Partition', 'target': 'CountEdges1'},
                {'source': 'Partition', 'target': 'CountEdges2'},
                {'source': 'Partition', 'target': 'CountEdges3'},
                {'source': 'CountEdges1', 'target': 'PageRank'},
                {'source': 'CountEdges2', 'target': 'PageRank'},
                {'source': 'CountEdges3', 'target': 'PageRank'},
                {'source': 'PageRank', 'target': 'ShortestPath'},
                {'source': 'ShortestPath', 'target': 'StoreResult'}
            ]
        }
        with open(dag_file, 'w') as f:
            json.dump(dag, f, indent=4)
        terminal.log("Initialized DAG with predefined nodes and edges.", level='INFO')
    
    return render_template('index.html', dag=dag)

@app.route('/web/update_dag', methods=['POST'])
def web_update_dag():
    """
    Receive updated DAG data from the web interface and save it.
    """
    global dag
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided.'}), 400
    
    if 'nodes' not in data or 'edges' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid data format.'}), 400
    
    dag = data
    save_dag()
    terminal.log("DAG updated via web interface.", level='INFO')
    return jsonify({'status': 'success'}), 200

def save_dag():
    """
    Save the current DAG to the DAG_FILE in JSON format.
    """
    dag_file = os.path.join(os.getcwd(), 'dag.json')
    try:
        with open(dag_file, 'w') as f:
            json.dump(dag, f, indent=4)
        terminal.log("DAG saved to dag.json.", level='INFO')
    except Exception as e:
        terminal.log(f"Failed to save DAG to dag.json: {e}", level='ERROR')

def flask_thread():
    """
    Run the Flask app. This function is intended to be run in a separate thread.
    """
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)  # Changed port to 5001 for web interface

class Master(Thread):
    """
    Master class that runs the Flask API, web interface, and manages the lifecycle.
    """
    def __init__(self):
        super().__init__()
        self.name = "Master"
        self.running = True
        self.terminal = Terminal.get_instance()
    
    def run(self):
        """
        Start the Flask server in a separate thread and manage lifecycle.
        """
        self.terminal.log(f"{self.name} started.", level='INFO')
        
        # Start Flask server for API and Web Interface
        server = Thread(target=flask_thread)
        server.start()
        self.terminal.log(f"{self.name} Flask server running on http://0.0.0.0:5001/ (Web Interface)", level='INFO')
        self.terminal.log(f"{self.name} Flask server running on http://0.0.0.0:5002/ (API)", level='INFO')
        
        # Start LifecycleManager (existing functionality)
        lifecycle_manager.initialize_cluster()
        lifecycle_manager.deploy_components()
        lifecycle_manager.receive_job()
        lifecycle_manager.optimize_job()
        lifecycle_manager.optimize_energy()
        lifecycle_manager.provision_resources()
        lifecycle_manager.initialize_runtime()
        lifecycle_manager.execute_job()
        lifecycle_manager.terminate()
        lifecycle_manager.reset()
        
        while self.running:
            time.sleep(1)
    
    def stop(self):
        """
        Stop the Master thread.
        """
        self.running = False
        self.terminal.log(f"{self.name} stopping.", level='INFO')
        # Flask server will stop when the main program exits

def main():
    """
    Entry point for the Master component.
    """
    terminal = Terminal.get_instance()
    terminal.start()
    try:
        master = Master()
        master.start()
        master.join()
    except KeyboardInterrupt:
        master.stop()
    finally:
        terminal.stop()

if __name__ == '__main__':
    main()