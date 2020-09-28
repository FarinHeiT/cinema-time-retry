from flask import Flask
from flask_socketio import SocketIO

import config
import redis

socketio = SocketIO(ping_interval=1, ping_timeout=2)
redis_db = redis.Redis(host='localhost', port=6379, db=0)


def create_app(debug=False):
    app = Flask(__name__, instance_relative_config=False)
    app.debug = debug
    app.config.from_object(config.Config)

    from .app import routes
    app.register_blueprint(routes.general)

    socketio.init_app(app)
    return app
