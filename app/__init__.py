from flask import Flask
from app.utils.constants import UPLOADS_FOLDER, RESULTS_FOLDER
from app.routes import routes  # Update if 'routes' is your blueprint

import os

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'))

    # Ensure the necessary folders exist
    os.makedirs(UPLOADS_FOLDER, exist_ok=True)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)

    # Register the blueprint
    app.register_blueprint(routes)

    return app
