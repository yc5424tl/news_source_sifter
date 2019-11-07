import os
import logging
import time
import itertools
import requests
from sifter.models import Source, Category


api_key = os.getenv('NEWS_SRC_MS_API_KEY')

logging.basicConfig(filename='news_sources_ms.log', level=logging.INFO)
logger = logging.getLogger(__name__)
# print(logging.getLoggerClass().root.handlers[0].baseFilename)

test_country_codes = {'ar': {'name': 'Argentina', 'language': 'es'}}

test_categories = ['sports']

categories = ['business', 'entertainment', 'health', 'science', 'sports', 'technology', 'general']

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



    def sift_sources(self):
        modified_src_id_set = set()  # Container for IDs of new/updated Sources
        top_data = self.request_top_sources()  # Request data from API
        if top_data:
            top_id_set = self.build_top_sources(top_data)  # Process data to create/update Category and Source records.
            modified_src_id_set.update(top_id_set)  # Track IDs of new/updated records
        time.sleep(240)
        # The APIs sources endpoint is limited to about 125 of the largest news sources globally.
        # These are the only sources (from 30,000) from the API which contain values
        # for  Country, Language, and Category -- and by extension to each their own articles.
        # However, the top-headlines endpoint has parameters for limiting
        # results to each of 54 available countires, as well as 7 categories.
        # Below, all combinations of countries/categories are used to query the API,
        # allowing for the indirect identification of a source's Country and Category/Categories,
        # while languages are applied by as 'most likely' for the given country.
        for country_code, category in itertools.product(test_country_codes, test_categories):
            country_data = self.request_country_sources(alpha2_code=country_code, src_cat=category)
            if country_data:
                country_src_id_set = self.build_country_sources(generated_country_sources=country_data, alpha2_code=country_code, src_cat=category)
                modified_src_id_set.update(country_src_id_set)
            time.sleep(240)
        data_dict = {'sources': [] for x in range(2)}  # Initialize container for new/updated Source JSON
        for src_id in modified_src_id_set:  # Use tracked Source IDs to populate JSON container
            src = Source.query.get(src_id)
            data_dict['sources'].append(src.json)
        try:
            payload = requests.post(url=os.getenv('NEWS_MAP_POST_URL'), json=data_dict, timeout=5)
            payload.raise_for_status()
            return True
        except ConnectionError:
            logger.log(level=logging.INFO, msg=f'ConnectionError when posting payload.')
            pass


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
        category = Category.query.filter_by(name=src_cat).first()
        if category is None:  # Category not in DB
            category = Category(name=src_cat)
            self.db.session.add(category)
            self.db.session.commit()
        for src in generated_country_sources:
            source = Source.query.filter_by(name=src["source"]["name"]).first()
            if source is None:  # Source does not exist in DB
                new_source = Source(name=src['source']['name'], country=alpha2_code, language=country_codes.get(alpha2_code).get('language'))
                new_source.categories.append(category)
                self.db.session.add(new_source)
                new_and_updated_id_set.add(new_source.id)
                logger.log(level=logging.INFO, msg=f'Adding source, NAME: {src["source"]["name"]}, COUNTRY: {alpha2_code}, LANGUAGE: {country_codes.get(alpha2_code).get("language")}, CATEGORY: {src_cat}')
                logger.log(level=logging.INFO, msg=f'Category {category} added to source -> {new_source.categories}')
            else:  # Source exists in DB
                try:  # Check if Category present for Source
                    idx = source.categories.index(category)
                except ValueError:  # Raised if not present, add Category to Source
                    source.categories.append(category)
                    new_and_updated_id_set.add(source.id)
                    logger.log(level=logging.INFO, msg=f'Category {category} added to source -> {source.categories}')
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
        new_and_updated_id_set = set()  # Store ID of each new Source and Sources with a new Category.
        for src in generated_top_sources:
            category = Category.query.filter_by(name=src['category']).first()  # Check DB for Category
            if category is None:  # Category does not exist in DB, add Category
                category = Category(name=src['category'])
                self.db.session.add(category)
                self.db.session.commit()
            source = Source.query.filter_by(name=src["name"]).first()  # Checking DB for Source
            if source is None:  # Source does not exist in DB, add Source.
                source = Source(name=src['name'], country=src['country'], language=src['language'])
                source.categories.append(category)
                self.db.session.add(source)
                new_and_updated_id_set.add(source.id)
            else:  # Source exists in DB.
                try:  # Check Source for Category
                    idx = source.categories.index(category)
                except ValueError:  # Category does not exist for Source, add Category.
                    source.categories.append(category)
                    new_and_updated_id_set.add(source.id)
        self.db.session.commit()
        return new_and_updated_id_set