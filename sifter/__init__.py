import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from flask_apscheduler import APScheduler
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config, ProductionConfig

logging.basicConfig(filename="news_sources_ms.log", level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
scheduler = APScheduler()


def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.app_context().push()

    db.init_app(app)
    from sifter import models

    db.create_all()
    db.session.commit()
    db.init_app(app)
    migrate.init_app(app, db)
    scheduler.init_app(app)

    if app.config["LOG_TO_STDOUT"]:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/news_source_sifter.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Launching Sifter")
    with app.app_context():

        try:
            return app
        except:
            logger.log(
                level=logging.INFO,
                msg="Returning app caused exception, shutting down scheduler.",
            )
            scheduler.shutdown()
