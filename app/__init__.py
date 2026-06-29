from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.storage import init_db

limiter = Limiter(
    get_remote_address,
    default_limits=[],
    storage_uri="memory://",
)


def create_app():
    app = Flask(__name__)

    limiter.init_app(app)
    init_db()

    from app.routes import api_bp
    app.register_blueprint(api_bp)

    return app
