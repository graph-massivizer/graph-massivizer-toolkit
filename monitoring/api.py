from flask import Blueprint, jsonify, current_app

api_bp = Blueprint('api', __name__)

@api_bp.route('/status')
def get_status():
    simulation = current_app.config['simulation']
    status = simulation.get_status()
    return jsonify(status)

@api_bp.route('/control/start', methods=['POST'])
def start_simulation():
    simulation = current_app.config['simulation']
    simulation.start_simulation()
    return jsonify({'message': 'Simulation started'})

@api_bp.route('/control/stop', methods=['POST'])
def stop_simulation():
    simulation = current_app.config['simulation']
    simulation.complete()
    return jsonify({'message': 'Simulation stopped'})