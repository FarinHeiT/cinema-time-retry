from flask import Flask
from flask_socketio import SocketIO

import config

socketio = SocketIO()

def create_app(debug=False):

    app = Flask(__name__, instance_relative_config=False)
    app.debug = debug
    app.config.from_object(config.Config)

    from .app import routes
    app.register_blueprint(routes.general)

    socketio.init_app(app)
    return app

