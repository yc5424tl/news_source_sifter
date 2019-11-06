import os
import logging
import time
import json
import itertools
import requests
from flask import session
from sifter.models import Source, Category
from sqlalchemy.exc import IntegrityError
import psycopg2


api_key = os.getenv('NEWS_SRC_MS_API_KEY')



logging.basicConfig(filename='news_sources_ms.log', level=logging.INFO)
logger = logging.getLogger(__name__)
# print(logging.getLoggerClass().root.handlers[0].baseFilename)

test_country_codes = {
    'ar': {'name': 'Argentina', 'language': 'es'},
    'au': {'name': 'Australia', 'language': 'en'}
}
categories = ['business', 'entertainment', 'health', 'science', 'sports', 'technology', None]
country_codes = {
    'ar': {'name':'Argentina',      'language': 'es'},
    'au': {'name':'Australia',      'language': 'en'},
    'at': {'name':'Austria',        'language': 'de'},
    'be': {'name':'Belgium',        'language': 'nl'},  # 'nl' most likely followed by 'fr', some 'de'
    'br': {'name':'Brazil',         'language': 'pt'},
    'bg': {'name':'Bulgaria',       'language': 'bg'},
    'ca': {'name':'Canada',         'language': 'en'},
    'cn': {'name':'China',          'language': 'zh'},
    'zh': {'name':'China',          'language': 'zh'},
    'co': {'name':'Columbia',       'language': 'es'},
    'cu': {'name':'Cuba',           'language': 'es'},
    'cz': {'name':'Czech Republic', 'language': 'cs'},
    'eg': {'name':'Egypt',          'language': 'ar'},
    'es': {'name':'Spain',          'language': 'es'},
    'fr': {'name':'France',         'language': 'fr'},
    'de': {'name':'Germany',        'language': 'de'},
    'gr': {'name':'Greece',         'language': 'el'},
    'hk': {'name':'Hong Kong',      'language': 'zh'},  # 'zh', some 'en'
    'hu': {'name':'Hungary',        'language': 'hu'},
    'in': {'name':'India',          'language': 'hi'},  # 'hi', 'en' ?
    'id': {'name':'Indonesia',      'language': 'id'},
    'ie': {'name':'Ireland',        'language': 'en'},
    'il': {'name':'Israel',         'language': 'he'},
    'is': {'name':'Israel',         'language': 'he'},  # 'he' + 'en'
    'it': {'name':'Italy',          'language': 'it'},
    'jp': {'name':'Japan',          'language': 'ja'},
    'lv': {'name':'Latvia',         'language': 'lv'},
    'lt': {'name':'Lithuania',      'language': 'lt'},
    'my': {'name':'Malaysia',       'language': 'ms'},  # 'ms' ? 'malay'
    'mx': {'name':'Mexico',         'language': 'es'},
    'ma': {'name':'Morocco',        'language': 'fr'},  # 'fr'most biz/gov/media, ar used more by population
    'nl': {'name':'Netherlands',    'language': 'nl'},
    'nz': {'name':'New Zealand',    'language': 'en'},
    'ng': {'name':'Nigeria',        'language': 'en'},
    'no': {'name':'Norway',         'language': 'no'},
    'pk': {'name':'Pakistan',       'language': 'ud'},
    'ph': {'name':'Philippines',    'language': 'en'},  # 'en' (none for filipino)
    'pl': {'name':'Poland',         'language': 'pl'},
    'pt': {'name':'Portugal',       'language': 'pt'},
    'ro': {'name':'Romania',        'language': 'ro'},
    'ru': {'name':'Russia',         'language': 'ru'},
    'sa': {'name':'Saudi Arabia',   'language': 'ar'},
    'rs': {'name':'Serbia',         'language': 'sr'},
    'sg': {'name':'Singapore',      'language': 'en'},  # 'en' (malay, ms, is official but en is used for biz/gov/edu)
    'sk': {'name':'Slovakia',       'language': 'sk'},
    'si': {'name':'Slovenia',       'language': 'sl'},
    'za': {'name':'South Africa',   'language': 'en'},
    'kr': {'name':'South Korea',    'language': 'ko'},
    'se': {'name':'Sweden',         'language': 'se'},  # 'se'=api  'sv'=iso
    'ch': {'name':'Switzerland',    'language': 'de'},  # 'de' @74%, other official: fr @ 21, it @ 4, and romansh @ 1)
    'tw': {'name':'Taiwan',         'language': 'zh'},
    'th': {'name':'Thailand',       'language': 'th'},
    'tr': {'name':'Turkey',         'language': 'tr'},
    'ae': {'name':'UAE',            'language': 'en'},
    'ua': {'name':'Ukraine',        'language': 'uk'},
    'gb': {'name':'United Kingdom', 'language': 'en'},
    'us': {'name':'United States',  'language': 'en'},
    've': {'name':'Venezuela',      'language': 'es'}
}


class SourceController:

    def __init__(self, db):
        self.db = db

    @staticmethod
    def generated_sources(src_gen):
        for src in src_gen:
            yield src


    def request_country_sources(self, alpha2_code, src_cat=None):
        if src_cat is None:
            endpoint = f'https://newsapi.org/v2/top-headlines?country={alpha2_code}&apiKey={api_key}'
        else:
            endpoint = f'https://newsapi.org/v2/top-headlines?country={alpha2_code}&category={src_cat}&apiKey={api_key}'
        response = requests.get(endpoint)
        if response.json()['status'] == 'ok':
            data = response.json()['articles']
            data_gen = (source for source in data)
            return self.generated_sources(data_gen)
        elif response.json()['status'] == 'error':
            logger.log(level=logging.ERROR, msg=f'Error Code: {response.json()["code"]} Message: {response.json()["message"]}')
            # raise Error
            return None


    def build_country_sources(self, generated_country_sources, alpha2_code, src_cat):
        new_and_updated_id_set = set()
        if src_cat is None:
            src_cat = 'unavailable'
        category = Category.query.filter_by(name=src_cat).first()
        if category is None:
            category = Category(name=src_cat)
            self.db.session.add(category)
            self.db.session.commit()
        for src in generated_country_sources:
            source = Source.query.filter_by(name=src["source"]["name"]).first()
            if source is None:
                new_source = Source(
                    name=src['source']['name'],
                    country=alpha2_code,
                    language=country_codes.get(alpha2_code).get('language'))
                logger.log(level=logging.INFO, msg=f'Adding source, NAME: {src["source"]["name"]}, COUNTRY: {alpha2_code}, LANGUAGE: {country_codes.get(alpha2_code).get("language")}, CATEGORY: {src_cat}')
                new_source.categories.append(category)
                logger.log(level=logging.INFO, msg=f'Category {category} added to source -> {new_source.categories}')
                self.db.session.add(new_source)
                new_and_updated_id_set.add(new_source.id)
                logger.log(level=logging.INFO, msg=f'Added {new_source.name} to DB and list.')
            else:
                logger.log(level=logging.INFO, msg=f'Established source has source.categories = {source.categories}, checking for {category}')

                try:
                    idx = source.categories.index(category)
                    logger.log(level=logging.INFO, msg=f'Category of {category} (ID:{category.id}, NAME:{category.name})'
                                                       f' already present in source.categories: {source.categories} {idx}')
                except ValueError:  # Raised when src_cat not in list source.categories
                    logger.log(level=logging.INFO, msg=f'Current source.categories: {source.categories}\nNew Category Name: {category.name}\n'
                                                       f'Target Category ID: {category.id}\nTarget Category Object: {category}')
                    source.categories.append(category)
                    new_and_updated_id_set.add(source.id)
                    logger.log(level=logging.INFO, msg=f'Source.categories after adding new cat: {source.categories}')
        self.db.session.commit()
        return new_and_updated_id_set

    @staticmethod
    def request_top_sources():
        response = requests.get(f"https://newsapi.org/v2/sources?apiKey={api_key}")
        if response.json()['status'] == 'ok':
            data = response.json()['sources']
            top_sources_gen = (source for source in data)
            return top_sources_gen
        elif response.json()['status'] == 'error':
            logger.log(level=logging.ERROR, msg=f'Code: {response.json()["code"]}, Message: {response.json()["message"]}')
            return None


    def build_top_sources(self, generated_top_sources):

        # Store ID of each new Source and Sources with a new Category.
        new_and_updated_id_set = set()

        for src in generated_top_sources:

            logger.log(level=logging.INFO, msg=f'src[category] = {src["category"]}\n src = {src}')
            # Check DB for Category
            category = Category.query.filter_by(name=src['category']).first()

            # Category does not exist in DB, add Category
            if category is None:
                category = Category(name=src['category'])

                self.db.session.add(category)
                self.db.session.commit()
            # Checking DB for Source
            source = Source.query.filter_by(name=src["name"]).first()

            # Source does not exist in DB, add Source.
            if source is None:
                source = Source(
                    name=src['name'],
                    country=src['country'],
                    language=src['language']
                )
                source.categories.append(category)
                self.db.session.add(source)
                new_and_updated_id_set.add(source.id)

            # Source exists in DB.
            else:
                # Check Source for Category
                try:
                    idx = source.categories.index(category)

                # Category does not exist for Source, add Category.
                except ValueError:
                    source.categories.append(category)
                    new_and_updated_id_set.add(source.id)

        self.db.session.commit()
        return new_and_updated_id_set



    def sift_sources(self):
        logger.log(level=logging.INFO, msg="Starting sift_sources")
        id_list = set()
        top_data = self.request_top_sources()
        logger.log(level=logging.INFO, msg=f'TOP DATA:\n {top_data}')
        if top_data:
            top_id_set = self.build_top_sources(top_data)
            id_list.difference_update(top_id_set)
        time.sleep(240)

        for country_code, category in itertools.product(test_country_codes, categories):
            logger.log(level=logging.INFO, msg=f'Requesting data from {country_code} of category {category}.')
            country_data = self.request_country_sources(alpha2_code=country_code, src_cat=category)
            if country_data:
                logger.log(level=logging.INFO, msg=f'Have {category} data from {country_code}.')
                country_src_id_set = self.build_country_sources(generated_country_sources=country_data, alpha2_code=country_code, src_cat=category)
                id_list.difference_update(country_src_id_set)
            time.sleep(240)

        data_dict = {'sources': []}
        for src_id in id_list:
            src = Source.query.get(src_id)
            # data_dict['sources'].append({
            #     'name': src.name,
            #     'country': src.country,
            #     'language': src.language,
            #     'categories': [category.name for category in src.categories]
            # })
            data_dict['sources'].append(src.json)
        json_data = json.dumps(data_dict)
        logger.log(level=logging.INFO, msg=f'JSON DATA ->\n\n\n{json_data}')
        print(json_data)
        return True


# if __name__ == '__main__':
#
#     scheduler.add_job(func=sift_sources, 'interval', minutes=2)
#     scheduler.start()
#     print(f'Press Ctrl+{"Break" if os.name == "nt" else "C"} to exit')
#     try:
#         while True:
#             time.sleep(2)
#     except (KeyboardInterrupt, SystemExit):
#         scheduler.shutdown()





# MISC

# There are two ways to add jobs to a scheduler:
#
#     by calling :meth:`~apscheduler.schedulers.base.BaseScheduler.add_job`
#     by decorating a function with :meth:`~apscheduler.schedulers.base.BaseScheduler.scheduled_job`
#
# The first way is the most common way to do it.
# The second way is mostly a convenience to declare jobs that don't change during the application's run time.
# The :meth:`~apscheduler.schedulers.base.BaseScheduler.add_job` method returns a
# :class:`apscheduler.job.Job` instance that you can use to modify or remove the job later.
#
# You can schedule jobs on the scheduler at any time. If the scheduler is not yet running when the job is added, the job will be scheduled tentatively and its first run time will only be computed when the scheduler starts.
#
# It is important to note that if you use an executor or job store that serializes the job, it will add a couple requirements on your job:
#     The target callable must be globally accessible
#     Any arguments to the callable must be serializable
#
# Of the builtin job stores, only MemoryJobStore doesn't serialize jobs.
# Of the builtin executors, only ProcessPoolExecutor will serialize jobs.
#
########################################################################################
# Important
#
# If you schedule jobs in a persistent job store during your application's initialization,
# you MUST define an explicit ID for the job and use replace_existing=True
# or you will get a new copy of the job every time your application restarts!
#



############################################################################
# Tip
#
# To run a job immediately, omit trigger argument when adding the job.


# SQALCHEMY JOBSTORE

# if __name__ == '__main__':
#     scheduler = BlockingScheduler()
#     url = sys.argv[1] if len(sys.argv) > 1 else 'sqlite:///example.sqlite'
#     scheduler.add_jobstore('sqlalchemy', url=url)
#     alarm_time = datetime.now() + timedelta(seconds=10)
#     scheduler.add_job(alarm, 'date', run_date=alarm_time, args=[datetime.now()])
#     print('To clear the alarms, delete the example.sqlite file.')
#     print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
#
#     try:
#         scheduler.start()
#     except (KeyboardInterrupt, SystemExit):
#         pass




# BACKGROUND SCHEDULER

# from datetime import datetime
# import time
# import os
#
# from apscheduler.schedulers.background import BackgroundScheduler
#
#
# def tick():
#     print('Tick! The time is: %s' % datetime.now())
#
#
# if __name__ == '__main__':
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(tick, 'interval', seconds=3)
#     scheduler.start()
#     print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
#
#     try:
#         # This is here to simulate application activity (which keeps the main thread alive).
#         while True:
#             time.sleep(2)
#     except (KeyboardInterrupt, SystemExit):
#         # Not strictly necessary if daemonic mode is enabled but should be done if possible
#         scheduler.shutdown()