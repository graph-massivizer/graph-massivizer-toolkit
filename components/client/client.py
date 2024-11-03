# components/client/client.py

from threading import Thread
from flask import Flask, render_template, request, redirect, url_for
from commons.terminal import Terminal
import time
import json

app = Flask(__name__)
terminal = Terminal.get_instance()

# In-memory representation of the DAG
dag = {
    'nodes': [],
    'edges': []
}

@app.route('/')
def index():
    return render_template('index.html', dag=dag)

@app.route('/add_node', methods=['POST'])
def add_node():
    node_id = request.form.get('node_id')
    if node_id and node_id not in dag['nodes']:
        dag['nodes'].append(node_id)
        terminal.log(f"Node {node_id} added to DAG.", level='INFO')
    return redirect(url_for('index'))

@app.route('/remove_node', methods=['POST'])
def remove_node():
    node_id = request.form.get('node_id')
    if node_id in dag['nodes']:
        dag['nodes'].remove(node_id)
        # Also remove edges associated with this node
        dag['edges'] = [edge for edge in dag['edges'] if edge[0] != node_id and edge[1] != node_id]
        terminal.log(f"Node {node_id} removed from DAG.", level='INFO')
    return redirect(url_for('index'))

@app.route('/add_edge', methods=['POST'])
def add_edge():
    from_node = request.form.get('from_node')
    to_node = request.form.get('to_node')
    if from_node in dag['nodes'] and to_node in dag['nodes']:
        edge = (from_node, to_node)
        if edge not in dag['edges']:
            dag['edges'].append(edge)
            terminal.log(f"Edge from {from_node} to {to_node} added to DAG.", level='INFO')
    return redirect(url_for('index'))

@app.route('/remove_edge', methods=['POST'])
def remove_edge():
    from_node = request.form.get('from_node')
    to_node = request.form.get('to_node')
    edge = (from_node, to_node)
    if edge in dag['edges']:
        dag['edges'].remove(edge)
        terminal.log(f"Edge from {from_node} to {to_node} removed from DAG.", level='INFO')
    return redirect(url_for('index'))

def flask_thread():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

class Client(Thread):
    def __init__(self):
        super().__init__()
        self.name = "Client"
        self.running = True
        self.terminal = Terminal.get_instance()

    def run(self):
        self.terminal.log(f"{self.name} started.", level='INFO')
        # Start Flask server
        server = Thread(target=flask_thread)
        server.start()
        while self.running:
            time.sleep(1)
            self.terminal.log(f"{self.name} is running the web interface.", level='DEBUG')

    def stop(self):
        self.running = False
        self.terminal.log(f"{self.name} stopping.", level='INFO')

def main():
    terminal = Terminal.get_instance()
    terminal.start()
    try:
        client = Client()
        client.start()
        client.join()
    except KeyboardInterrupt:
        client.stop()
    finally:
        terminal.stop()

if __name__ == '__main__':
    main()