import logging

from flask import Flask
from flask_apscheduler import APScheduler
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

logging.basicConfig(filename='news_sources_ms.log', level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()
migrate = Migrate()
scheduler = APScheduler()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.app_context().push()

    db.init_app(app)
    from sifter import models
    db.create_all()

    migrate.init_app(app, db)
    scheduler.init_app(app)

    with app.app_context():
        from sifter.source_controller import SourceController
        transcriber = SourceController(db)
        scheduler.add_job(transcriber.sift_sources(), 'interval', minutes=2)
        scheduler.start()
        try:
            return app
        except:
            logger.log(level=logging.INFO, msg="Returning app caused exception, shutting down scheduler.")
            scheduler.shutdown()