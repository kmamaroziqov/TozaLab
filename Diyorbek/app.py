from flask import Flask
from config import Config
from app.models import db
from app.routes import main

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main)

    return app