from flask import Flask

from app.storage import init_db


def create_app():
    app = Flask(__name__)

    init_db()

    from app.routes import submit_bp
    app.register_blueprint(submit_bp)

    return app
