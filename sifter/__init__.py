
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_apscheduler import APScheduler
from sqlalchemy.orm import Session
import logging

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
    # from sifter.models import Source, Category
    db.create_all()
    # db.session.commit()
    migrate.init_app(app, db)
    scheduler.init_app(app)


    with app.app_context():
        from sifter.source_controller import SourceController
        transcriber = SourceController(db)
        scheduler.add_job(transcriber.sift_sources(), 'interval', minutes=2)
        logger.log(level=logging.INFO, msg="Initialized Scheduler and added Job")

        from sifter.models import Category
        for cat in ['business', 'entertainment', 'health', 'sports', 'science', 'technology', 'unavailable']:
            print(f'checking category {cat}')
            record = Category.query.filter_by(name=cat).first()
            if record is None:
                print(f'making new cat {cat}')
                new_cat = Category(name=cat)
                db.session.add(new_cat)
        db.session.commit()

        scheduler.start()
            # print('in app context')
            # from sifter.models import Category, Source
            # from sifter import schedule
            # context = current_app._get_current_object()
            # scheduler.add_job(schedule.sift_sources, 'interval', minutes=1, app=context)
            # scheduler.start()
        try:
            logger.log(level=logging.INFO, msg="Returning app from create_app")
            return app
        except:
            logger.log(level=logging.INFO, msg="Returning app caused exception, shutting down scheduler.")
            scheduler.shutdown()