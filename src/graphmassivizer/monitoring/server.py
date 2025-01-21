from flask import Flask
from graphmassivizer.monitoring.dashboard import dashboard_bp
from graphmassivizer.monitoring.api import api_bp

from flask.app import Flask


def create_app(simulation) -> Flask:
    app = Flask(__name__)

    # Register Blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Pass the simulation object to Flask
    app.config['simulation'] = simulation

    return app
