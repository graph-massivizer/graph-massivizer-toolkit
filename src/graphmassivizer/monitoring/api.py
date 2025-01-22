from typing import Any, cast
from flask import Blueprint, jsonify, current_app

api_bp = Blueprint('api', __name__)


# TODO This needs to be upgrades so that more information can make it to the dashboard. Now Mocked.

class LifeCycleWrapper:
    def get_status(self) -> tuple[str, list[dict[str, Any]]]:
        raise NotImplementedError()

    def start_simulation(self) -> None:
        raise NotImplementedError()

    def complete(self) -> None:
        raise NotImplementedError()


def _get_simulation() -> LifeCycleWrapper:
    simulation = cast(LifeCycleWrapper, current_app.config['simulation'])
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
