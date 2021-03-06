from sifter import create_app, scheduler, db
import os

import json
import random
import requests
import time
import logging




api_key = os.getenv('NEWS_SRC_MS_API_KEY')
logging.basicConfig(filename='news_sources_ms.log', level=logging.INFO)
logger = logging.getLogger(__name__)
categories = ['business', 'entertainment', 'health', 'science', 'sports', 'technology', 'general']

api_country_codes = {
    'ar': {'name':'Argentina',      'language': 'es'},
    'au': {'name':'Australia',      'language': 'en'},
    'at': {'name':'Austria',        'language': 'de'},
    'be': {'name':'Belgium',        'language': 'nl'},  # 'nl' most likely followed by 'fr', some 'de'
    'br': {'name':'Brazil',         'language': 'pt'},
    'bg': {'name':'Bulgaria',       'language': 'bg'},
    'ca': {'name':'Canada',         'language': 'en'},
    'cn': {'name':'China',          'language': 'zh'},
    'co': {'name':'Columbia',       'language': 'es'},
    'cu': {'name':'Cuba',           'language': 'es'},
    'cz': {'name':'Czech Republic', 'language': 'cs'},
    'eg': {'name':'Egypt',          'language': 'ar'},
    'fr': {'name':'France',         'language': 'fr'},
    'de': {'name':'Germany',        'language': 'de'},
    'gr': {'name':'Greece',         'language': 'el'},
    'hk': {'name':'Hong Kong',      'language': 'zh'},
    'hu': {'name':'Hungary',        'language': 'hu'},
    'in': {'name':'India',          'language': 'hi'},
    'id': {'name':'Indonesia',      'language': 'id'},
    'ie': {'name':'Ireland',        'language': 'en'},
    'il': {'name':'Israel',         'language': 'he'},
    'it': {'name':'Italy',          'language': 'it'},
    'jp': {'name':'Japan',          'language': 'ja'},
    'lv': {'name':'Latvia',         'language': 'lv'},
    'lt': {'name':'Lithuania',      'language': 'lt'},
    'my': {'name':'Malaysia',       'language': 'ms'},
    'mx': {'name':'Mexico',         'language': 'es'},
    'ma': {'name':'Morocco',        'language': 'fr'},  # 'fr'most biz/gov/media, ar used more by population
    'nl': {'name':'Netherlands',    'language': 'nl'},
    'nz': {'name':'New Zealand',    'language': 'en'},
    'ng': {'name':'Nigeria',        'language': 'en'},
    'no': {'name':'Norway',         'language': 'no'},
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
    'se': {'name':'Sweden',         'language': 'se'},
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

country_codes = {

    'zh': {'name':'China',          'language': 'zh'},
    'es': {'name':'Spain',          'language': 'es'},
    'is': {'name':'Israel',         'language': 'he'},  # 'he' + 'en'     < ICELAND >
    'pk': {'name':'Pakistan',       'language': 'ud'},
    'ch': {'name':'Switzerland',    'language': 'de'},  # 'de' @74%, other official: fr @ 21, it @ 4, and romansh @ 1)


    # ONLY THE 2 LETTER CODE IS IN FOR THESE
    'bo':{'Bolivia'},
    'by':{'Belarus'},
    'cl':{'Chile'},
    'ci':{"Cote d'Ivoire"},
    'cr':{'Costa Rica'},
    'ec':{'Ecuador'},
    'fi':{'Finland'},
    'gt':{'Guatamala'},
    'hn':{'honduras'},
    'kz':{'Kazakhstan'},
    'lu':{'Luxembourg'},
    'pa':{'Panama'},
    'pe':{'Peru'},
    'ug':{'Uganda'},
    'uy':{'Uruguay'},
}

NOT_ENTERED_AT_ALL = {
    'ad':'Andorra',
    'af':'Afghanistan',
    'al':'Albania',
    'am':'Armenia',
    'ao':'Angola',
    'as':'American Samoa',
    'az':'Azerbaijan',
    'ba':'Bosnia and Herzegovina',
    'bd':'Bangladesh',
    'bf':'Burkina Faso',
    'bh':'Bahrain',
    'bi':'Burundi',
    'bj':'Benin',
    'bt':'Bhutan',
    'bw':'Botswana',
    'bz':'Belize',
    'cd':'Congo, Democratic Republic of the',
    'cf':'Central African Republic',
    'cg':'Congo',
    'cm':'Cameroon',
    'cy':'Cyprus',
    'cz':'Czech Republic',
    'dj':'Djibouti',
    'dk':'Denmark',
    'do':'Dominican Republic',
    'dz':'Algeria',
    'ee':'Estonia',
    'er':'Eritrea',
    'et':'Ethiopia',
    'fj':'Fiji',
    'ga':'Gabon',
    'gd':'Grenada',
    'ge':'Georgia',
    'gf':'French Guiana',
    'gh':'Ghana',
    'gi':'Gibraltar',
    'gl':'Greenland',
    'gm':'Gambia',
    'gn':'Guinea',
    'gp':'Guadeloupe',
    'gq':'Equatorial Guinea',
    'gs':'South Georgia',
    'gu':'Guam',
    'gw':'Guinea-Bissau',
    'gy':'Guyana',
    'hr':'Croatia',
    'ht':'Haiti',
    'iq':'Iraq',
    'ir':'Iran',
    'is':'Iceland',
    'jm':'Jamaica',
    'jo':'Jordan',
    'ke':'Kenya',
    'kg':'Kyrgyzstan',
    'kh':'Cambodia',
    'kp':'North Korea',
    'kw':'Kuwait',
    'la':'Laos',
    'lb':'Lebanon',
    'li':'Liechtenstein',
    'lk':'Sri Lanka',
    'lr':'Liberia',
    'ls':'Lesotho',
    'lt':'Lithuania',
    'ly':'Libya',
    'mc':'Monaco',
    'md':'Moldova',
    'me':'Montenegro',
    'mg':'Madagascar',
    'mk':'North Macedonia',
    'ml':'Mali',
    'mm':'Myanmar',
    'mn':'Mongolia',
    'mr':'Mauritania',
    'mt':'Malta',
    'mu':'Mauritius',
    'mv':'Maldives',
    'mw':'Malawi',
    'mz':'Mozambique',
    'na':'Namibia',
    'ne':'Niger',
    'ng':'Nigeria',
    'ni':'Nicaragua',
    'np':'Nepal',
    'om':'Oman',
    'pf':'French Polynesia',
    'pg':'Papua New Guinea',
    'ps':'Palestine',
    'qa':'Qatar',
    'rw':'Rwanda',
    'sd':'Sudan',
    'sl':'Sierra Leone',
    'sn':'Senegal',
    'so':'Somalia',
    'sr':'Suriname',
    'ss':'South Sudan',
    'sv':'El Salvador',
    'sy':'Syria',
    'td':'Chad',
    'tg':'Togo',
    'tj':'Tajikistan',

}

data_dict = {'sources': [] for x in range(2)}
bool_dict = {'have_top': False}




def populate_categories():
    for category in categories:
        cat = Category.query.filter_by(name=category).first()
        if not cat:
            new_category = Category(name=category)
            db.session.add(new_category)
    db.session.commit()



def sift_sources():
    with app.app_context():

        modified_src_id_set = set()  # Container for IDs of new/updated Sources

        first_category = Category.query.filter_by(id=1).first()
        if not first_category:
            populate_categories()

        print('sifting sources')
        first_source = Source.query.filter_by(id=1).first()
        print(f'first_source = {first_source}')
        if not first_source:
            try:
                with open("./static/js/top_sources.json") as json_data:
                    print(f'file open')
                    data = json.load(json_data)['sources']
                    print(f'json.load(json_data) == {data}')
                    for source_data in data:
                        category = Category.query.filter_by(name=source_data['category']).first()
                        new_source = Source(name=source_data['name'],
                                            country=source_data['country'],
                                            language=source_data['language'],
                                            url=source_data['url'],
                                            categories = [category])
                        db.session.add(new_source)
                        db.session.commit()
                        modified_src_id_set.add(new_source.id)
            except FileNotFoundError:
                logger.log(level=logging.INFO, msg='Error Building Sources from File.')

        print('passed if not first source try/except')

        # The APIs sources endpoint is limited to about 125 of the largest news sources globally.
        # These are the only sources (from 30,000) from the API which contain values
        # for  Country, Language, and Category -- and by extension to each their own articles.
        # However, the top-headlines endpoint has parameters for limiting
        # results to each of 54 available countires, as well as 7 categories.
        # Below, all combinations of countries/categories are used to query the API,
        # allowing for the indirect identification of a source's Country and Category/Categories,
        # while languages are applied by as 'most likely' for the given country.

        target_list = list(country_codes.keys())
        random_target = random.choice(target_list)
        random_category = random.choice(categories)
        country_data = request_country_sources(alpha2_code=random_target, src_cat=random_category)

        if country_data:
            country_src_id_set = build_country_sources(
                generated_country_sources=country_data, alpha2_code=random_target, src_cat=random_category)
            modified_src_id_set.update(country_src_id_set)

        # CODE BELOW IS FOR USE IF NOT RATE LIMITED BY API

        # top_data = request_top_sources()  # Request data from API
        # if top_data:
        #     top_id_set = build_top_sources(top_data)  # Process data to create/update Category and Source records.
        #     modified_src_id_set.update(top_id_set)  # Track IDs of new/updated records

        # time.sleep(240)
        # for country_code, category in itertools.product(country_codes, categories):
            # country_data = request_country_sources(alpha2_code=country_code, src_cat=category)
            # if country_data:
            #     country_src_id_set = build_country_sources(
            #         generated_country_sources=country_data, alpha2_code=country_code, src_cat=category)
            #     modified_src_id_set.update(country_src_id_set)
            # time.sleep(240)

        for src_id in modified_src_id_set:  # Use tracked Source IDs to populate JSON container
            src = Source.query.filter_by(id=src_id).first()
            data_dict['sources'].append(src.json)
        try:
            payload = post_json(data_dict)
            logger.log(level=logging.INFO, msg=f'Payload Delivered == {payload}\n\n=================================================\nContents:\n{data_dict}\n\n=================================================\n')
            time.sleep(360)
            return True
        except ConnectionError:
            logger.log(level=logging.INFO, msg=f'ConnectionError when posting payload.')
            return False



print('creating app')
app = create_app()
scheduler.add_job(id='sifter_scheduler', func=sift_sources, trigger='interval', minutes=6)
scheduler.start()
app.app_context().push()
from sifter.models import Source, Category, source_categories



@app.shell_context_processor
def make_shell_context():
    return {'db': app.db, 'Source': Source, 'Category': Category}



@app.route('/stay_alive')
def stay_alive():
    logger.log(level=logging.INFO, msg='STAY ALIVE RECEIVED')
    print('STAYIN ALIVE')
    return json.dumps({'stay':'alive'}), 200, {'ContentType':'application/json'}



def post_json(payload: dict):
    login_url = os.getenv('NEWS_MAP_LOGIN_URL')
    username  = os.getenv('NEWS_MAP_POST_USER')
    password  = os.getenv('NEWS_MAP_POST_PW')
    post_url  = os.getenv('NEWS_MAP_POST_URL')

    client = requests.session()
    client.get(login_url)
    csrf_token = client.cookies['csrftoken']

    login_data = {'username':username, 'password':password, 'csrfmiddlewaretoken':csrf_token, 'next':'/'}

    r1 = client.post(login_url, data=login_data, headers=dict(Referer=login_url))
    logger.log(level=logging.INFO, msg=f'response_1 => {r1}')

    r2 = client.post(url=post_url, json=payload)
    logger.log(level=logging.INFO, msg=f'response_2 => {r2}')

    return True



def post_sources():
    login_url = os.getenv('NEWS_MAP_LOGIN_URL')
    username = os.getenv('NEWS_MAP_POST_USER')
    password = os.getenv('NEWS_MAP_POST_PW')























































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































def generated_sources(src_gen):
    for src in src_gen:
        yield src



def request_country_sources(alpha2_code, src_cat=None):

    if src_cat is None:
        endpoint = f'https://newsapi.org/v2/top-headlines?country={alpha2_code}&apiKey={api_key}'
    else:
        endpoint = f'https://newsapi.org/v2/top-headlines?country={alpha2_code}&category={src_cat}&apiKey={api_key}'

    response = requests.get(endpoint)

    if response.json()['status'] == 'ok':
        data = response.json()['articles']
        data_gen = (source for source in data)
        return generated_sources(data_gen)

    elif response.json()['status'] == 'error':
        logger.log(level=logging.ERROR, msg=f'Error Code: {response.json()["code"]} Message: {response.json()["message"]}')
        # raise Error
        return None



def build_country_sources(generated_country_sources, alpha2_code, src_cat):

    new_and_updated_id_set = set()
    category = Category.query.filter_by(name=src_cat).first()

    if category is None:  # Category not in DB
        category = Category(name=src_cat)
        db.session.add(category)
        db.session.commit()

    for src in generated_country_sources:
        source = Source.query.filter_by(name=src["source"]["name"]).first()

        if source is None:  # Source does not exist in DB
            new_source = Source(name=src['source']['name'], country=alpha2_code, language=country_codes.get(alpha2_code).get('language'))
            new_source.categories.append(category)
            db.session.add(new_source)
            db.session.commit()
            new_and_updated_id_set.add(new_source.id)
            logger.log(level=logging.INFO, msg=f'Adding source, NAME: {src["source"]["name"]}, COUNTRY: {alpha2_code}, LANGUAGE: {country_codes.get(alpha2_code).get("language")}, CATEGORY: {src_cat}')
            logger.log(level=logging.INFO, msg=f'Category {category} added to source -> {new_source.categories}')

        else:  # Source exists in DB
            try:  # Check if Category present for Source
                idx = source.categories.index(category)
            except ValueError:  # Raised if not present, add Category to Source
                source.categories.append(category)
                db.session.commit()
                new_and_updated_id_set.add(source.id)
                logger.log(level=logging.INFO, msg=f'Category {category} added to source -> {source.categories}')

    db.session.commit()
    return new_and_updated_id_set



def request_top_sources():
    response = requests.get(f"https://newsapi.org/v2/sources?apiKey={api_key}")

    if response.json()['status'] == 'ok':
        data = response.json()['sources']
        top_sources_gen = (source for source in data)
        return top_sources_gen

    elif response.json()['status'] == 'error':
        logger.log(level=logging.ERROR, msg=f'Code: {response.json()["code"]}, Message: {response.json()["message"]}')
        return None



def build_top_sources(generated_top_sources):

    new_and_updated_id_set = set()  # Store ID of each new Source and Sources with a new Category.

    for src in generated_top_sources:

        category = Category.query.filter_by(name=src['category']).first()  # Check DB for Category[
        if category is None:  # Category does not exist in DB, add Category
            category = Category(name=src['category'])
            db.session.add(category)
            db.session.commit()

        source = Source.query.filter_by(name=src["name"]).first()  # Checking DB for Source
        if source is None:  # Source does not exist in DB, add Source.
            source = Source(name=src['name'], country=src['country'], language=src['language'])
            source.categories.append(category)
            db.session.add(source)
            db.session.commit()
            new_and_updated_id_set.add(source.id)
        else:  # Source exists in DB.
            try:  # Check Source for Category
                idx = source.categories.index(category)
            except ValueError:  # Category does not exist for Source, add Category.
                source.categories.append(category)
                db.session.commit()
                new_and_updated_id_set.add(source.id)

    db.session.commit()
    return new_and_updated_id_set



def differential_import():
    sources = Source.query.all()
    source_data = {'sources': [source.json for source in sources]}
    print(f'DIFFERENTIAL SOURCE DATA:\n{source_data}')
    post_json(source_data)
    print('differential_import complete')



def export_all_data():

    srcs = Source.query.all()
    cats = Category.query.all()
    # src_cats = Source.categories.through.objects.all()
    src_cats = db.session.query(source_categories.c.all())


    source_data = {'sources': [source.json for source in srcs]}
    category_data = {'categories': [category.json for category in cats]}
    src_cats_data = {'src_cats': [src_cat.json for src_cat in src_cats]}

    #sources_posted = post_sources()
    #categories_posted = post_categories()