import logging
from logging.handlers import RotatingFileHandler
import os
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
    app.config.from_object(os.getenv('APP_SETTINGS'))
    app.app_context().push()

    db.init_app(app)
    from sifter import models
    db.create_all()

    migrate.init_app(app, db)
    scheduler.init_app(app)

    if app.config['LOG_TO_STDOUT']:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
    else:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/news_source_sifter.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Launching Sifter')
    with app.app_context():

        try:
            return app
        except:
            logger.log(level=logging.INFO, msg="Returning app caused exception, shutting down scheduler.")
            scheduler.shutdown()


# def sift_sources():
#     import sifter.source_controller as controller
#     from sifter.models import Source
#     modified_src_id_set = set()  # Container for IDs of new/updated Sources
#     top_data = controller.request_top_sources()  # Request data from API
#     if top_data:
#         top_id_set = controller.build_top_sources(top_data, db)  # Process data to create/update Category and Source records.
#         modified_src_id_set.update(top_id_set)  # Track IDs of new/updated records
#     # time.sleep(240)
#     time.sleep(30)
#
#     # The APIs sources endpoint is limited to about 125 of the largest news sources globally.
#     # These are the only sources (from 30,000) from the API which contain values
#     # for  Country, Language, and Category -- and by extension to each their own articles.
#     # However, the top-headlines endpoint has parameters for limiting
#     # results to each of 54 available countires, as well as 7 categories.
#     # Below, all combinations of countries/categories are used to query the API,
#     # allowing for the indirect identification of a source's Country and Category/Categories,
#     # while languages are applied by as 'most likely' for the given country.
#     for country_code, category in itertools.product(controller.test_country_codes, controller.test_categories):
#         country_data = controller.request_country_sources(alpha2_code=country_code, src_cat=category)
#         if country_data:
#             country_src_id_set = controller.build_country_sources(generated_country_sources=country_data, alpha2_code=country_code, src_cat=category, db=db)
#             modified_src_id_set.update(country_src_id_set)
#         time.sleep(120)
#     print('done getting data, building payload')
#     # data_dict = {'sources': [] for x in range(2)}  # Initialize container for new/updated Source JSON
#     for src_id in modified_src_id_set:  # Use tracked Source IDs to populate JSON container
#         src = Source.query.filter_by(id=src_id).first()
#         controller.data_dict['sources'].append(src.json)
#     try:
#         print('sending payload')
#         # payload = requests.post(url=os.getenv('NEWS_MAP_POST_URL'), json=data_dict, auth=(os.getenv('SIFTER_POST_USER'), os.getenv('SIFTER_POST_PASS')), timeout=5)
#         # payload.raise_for_status()
#         payload = controller.post_json(controller.data_dict)
#         logger.log(level=logging.INFO, msg=f'Payload Delivered == {payload}\n\n'
#                                            f'=================================================\n'
#                                            f'Contents:\n{controller.data_dict}\n\n'
#                                            f'=================================================\n')
#         return True
#     except ConnectionError:
#         logger.log(level=logging.INFO, msg=f'ConnectionError when posting payload.')
#         pass
