from flask import Flask
from config.config import Config
from application.db.db import db
from application.service.create_default_service import CreateDefaultService


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    from application.route.route import user_bp
    app.register_blueprint(user_bp)

    with app.app_context():
        db.create_all()
        CreateDefaultService().create_def_users()


    return app