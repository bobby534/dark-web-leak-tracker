from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-secret")

    from app.routes import main
    app.register_blueprint(main)

    return app
