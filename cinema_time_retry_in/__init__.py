from flask import Flask
import config
from cinema_time_retry_in import routes

app = Flask(__name__, instance_relative_config=False)
app.config.from_object(config.Config)

app.register_blueprint(routes.general)

