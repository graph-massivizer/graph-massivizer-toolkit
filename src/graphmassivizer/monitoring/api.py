from typing import cast
from flask import Blueprint, jsonify, current_app

from graphmassivizer.simulation.lifecycle import SimulationLifecycle

api_bp = Blueprint('api', __name__)


def _get_simulation() -> SimulationLifecycle:
    simulation = cast(SimulationLifecycle, current_app.config['simulation'])
    return simulation


@api_bp.route('/status')
def get_status():
    status = _get_simulation().get_status()
    return jsonify(status)


@api_bp.route('/control/start', methods=['POST'])
def start_simulation():
    simulation = _get_simulation()
    simulation.start_simulation()
    return jsonify({'message': 'Simulation started'})


@api_bp.route('/control/stop', methods=['POST'])
def stop_simulation():
    simulation = _get_simulation()
    simulation.complete()
    return jsonify({'message': 'Simulation stopped'})
