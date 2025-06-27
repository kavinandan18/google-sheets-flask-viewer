from flask import Flask
from flask_session import Session

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "f6e1c48b6b5f4e0a8dc1e4e028e7865089421762c6b79f35"
    app.config["SESSION_TYPE"] = "filesystem"  # Store session data on filesystem
    Session(app)  # Initialize session

    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app