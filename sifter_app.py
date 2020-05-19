from sifter import create_app, scheduler, db
import os


import json
import random
import requests
import time
import logging

api_key = os.getenv("NEWS_SRC_MS_API_KEY")
logging.basicConfig(filename="news_sources_ms.log", level=logging.INFO)
logger = logging.getLogger(__name__)

categories = [
    "business",
    "entertainment",
    "health",
    "science",
    "sports",
    "technology",
    "general",
]

api_country_codes = {
    "ar": {"name": "Argentina", "language": "es"},
    "au": {"name": "Australia", "language": "en"},
    "at": {"name": "Austria", "language": "de"},
    "be": {
        "name": "Belgium",
        "language": "nl",
    },  # 'nl' most likely followed by 'fr', some 'de'
    "br": {"name": "Brazil", "language": "pt"},
    "bg": {"name": "Bulgaria", "language": "bg"},
    "ca": {"name": "Canada", "language": "en"},
    "cn": {"name": "China", "language": "zh"},
    "co": {"name": "Columbia", "language": "es"},
    "cu": {"name": "Cuba", "language": "es"},
    "cz": {"name": "Czech Republic", "language": "cs"},
    "eg": {"name": "Egypt", "language": "ar"},
    "fr": {"name": "France", "language": "fr"},
    "de": {"name": "Germany", "language": "de"},
    "gr": {"name": "Greece", "language": "el"},
    "hk": {"name": "Hong Kong", "language": "zh"},
    "hu": {"name": "Hungary", "language": "hu"},
    "in": {"name": "India", "language": "hi"},
    "id": {"name": "Indonesia", "language": "id"},
    "ie": {"name": "Ireland", "language": "en"},
    "il": {"name": "Israel", "language": "he"},
    "it": {"name": "Italy", "language": "it"},
    "jp": {"name": "Japan", "language": "ja"},
    "lv": {"name": "Latvia", "language": "lv"},
    "lt": {"name": "Lithuania", "language": "lt"},
    "my": {"name": "Malaysia", "language": "ms"},
    "mx": {"name": "Mexico", "language": "es"},
    "ma": {
        "name": "Morocco",
        "language": "fr",
    },  # 'fr'most biz/gov/media, ar used more by population
    "nl": {"name": "Netherlands", "language": "nl"},
    "nz": {"name": "New Zealand", "language": "en"},
    "ng": {"name": "Nigeria", "language": "en"},
    "no": {"name": "Norway", "language": "no"},
    "ph": {"name": "Philippines", "language": "en"},  # 'en' (none for filipino)
    "pl": {"name": "Poland", "language": "pl"},
    "pt": {"name": "Portugal", "language": "pt"},
    "ro": {"name": "Romania", "language": "ro"},
    "ru": {"name": "Russia", "language": "ru"},
    "sa": {"name": "Saudi Arabia", "language": "ar"},
    "rs": {"name": "Serbia", "language": "sr"},
    "sg": {
        "name": "Singapore",
        "language": "en",
    },  # 'en' (malay, ms, is official but en is used for biz/gov/edu)
    "sk": {"name": "Slovakia", "language": "sk"},
    "si": {"name": "Slovenia", "language": "sl"},
    "za": {"name": "South Africa", "language": "en"},
    "kr": {"name": "South Korea", "language": "ko"},
    "se": {"name": "Sweden", "language": "se"},
    "ch": {
        "name": "Switzerland",
        "language": "de",
    },  # 'de' @74%, other official: fr @ 21, it @ 4, and romansh @ 1)
    "tw": {"name": "Taiwan", "language": "zh"},
    "th": {"name": "Thailand", "language": "th"},
    "tr": {"name": "Turkey", "language": "tr"},
    "ae": {"name": "UAE", "language": "en"},
    "ua": {"name": "Ukraine", "language": "uk"},
    "gb": {"name": "United Kingdom", "language": "en"},
    "us": {"name": "United States", "language": "en"},
    "ve": {"name": "Venezuela", "language": "es"},
}

country_codes = {
    "zh": {"name": "China", "language": "zh"},
    "es": {"name": "Spain", "language": "es"},
    "is": {"name": "Israel", "language": "he"},  # 'he' + 'en'     < ICELAND >
    "pk": {"name": "Pakistan", "language": "ud"},
    "ch": {
        "name": "Switzerland",
        "language": "de",
    },  # 'de' @74%, other official: fr @ 21, it @ 4, and romansh @ 1)
    # ONLY THE 2 LETTER CODE IS IN FOR THESE
    "bo": {"Bolivia"},
    "by": {"Belarus"},
    "cl": {"Chile"},
    "ci": {"Cote d'Ivoire"},
    "cr": {"Costa Rica"},
    "ec": {"Ecuador"},
    "fi": {"Finland"},
    "gt": {"Guatamala"},
    "hn": {"honduras"},
    "kz": {"Kazakhstan"},
    "lu": {"Luxembourg"},
    "pa": {"Panama"},
    "pe": {"Peru"},
    "ug": {"Uganda"},
    "uy": {"Uruguay"},
}

NOT_ENTERED_AT_ALL = {
    "ad": "Andorra",
    "af": "Afghanistan",
    "al": "Albania",
    "am": "Armenia",
    "ao": "Angola",
    "as": "American Samoa",
    "az": "Azerbaijan",
    "ba": "Bosnia and Herzegovina",
    "bd": "Bangladesh",
    "bf": "Burkina Faso",
    "bh": "Bahrain",
    "bi": "Burundi",
    "bj": "Benin",
    "bt": "Bhutan",
    "bw": "Botswana",
    "bz": "Belize",
    "cd": "Congo, Democratic Republic of the",
    "cf": "Central African Republic",
    "cg": "Congo",
    "cm": "Cameroon",
    "cy": "Cyprus",
    "cz": "Czech Republic",
    "dj": "Djibouti",
    "dk": "Denmark",
    "do": "Dominican Republic",
    "dz": "Algeria",
    "ee": "Estonia",
    "er": "Eritrea",
    "et": "Ethiopia",
    "fj": "Fiji",
    "ga": "Gabon",
    "gd": "Grenada",
    "ge": "Georgia",
    "gf": "French Guiana",
    "gh": "Ghana",
    "gi": "Gibraltar",
    "gl": "Greenland",
    "gm": "Gambia",
    "gn": "Guinea",
    "gp": "Guadeloupe",
    "gq": "Equatorial Guinea",
    "gs": "South Georgia",
    "gu": "Guam",
    "gw": "Guinea-Bissau",
    "gy": "Guyana",
    "hr": "Croatia",
    "ht": "Haiti",
    "iq": "Iraq",
    "ir": "Iran",
    "is": "Iceland",
    "jm": "Jamaica",
    "jo": "Jordan",
    "ke": "Kenya",
    "kg": "Kyrgyzstan",
    "kh": "Cambodia",
    "kp": "North Korea",
    "kw": "Kuwait",
    "la": "Laos",
    "lb": "Lebanon",
    "li": "Liechtenstein",
    "lk": "Sri Lanka",
    "lr": "Liberia",
    "ls": "Lesotho",
    "lt": "Lithuania",
    "ly": "Libya",
    "mc": "Monaco",
    "md": "Moldova",
    "me": "Montenegro",
    "mg": "Madagascar",
    "mk": "North Macedonia",
    "ml": "Mali",
    "mm": "Myanmar",
    "mn": "Mongolia",
    "mr": "Mauritania",
    "mt": "Malta",
    "mu": "Mauritius",
    "mv": "Maldives",
    "mw": "Malawi",
    "mz": "Mozambique",
    "na": "Namibia",
    "ne": "Niger",
    "ng": "Nigeria",
    "ni": "Nicaragua",
    "np": "Nepal",
    "om": "Oman",
    "pf": "French Polynesia",
    "pg": "Papua New Guinea",
    "ps": "Palestine",
    "qa": "Qatar",
    "rw": "Rwanda",
    "sd": "Sudan",
    "sl": "Sierra Leone",
    "sn": "Senegal",
    "so": "Somalia",
    "sr": "Suriname",
    "ss": "South Sudan",
    "sv": "El Salvador",
    "sy": "Syria",
    "td": "Chad",
    "tg": "Togo",
    "tj": "Tajikistan",
}


def sift_sources():

    with app.app_context():

        if verify_base_categories() and verify_base_sources():
            countries = list(api_country_codes.keys())
            random_country = random.choice(countries)
            print(f'random country = {random_country}')

            random_category = random.choice(categories)
            print(f'random category = {random_category}')
            sources_for_country = request_country_sources(
                alpha2_code=random_country, src_cat=random_category
            )
            if sources_for_country:
                src_ids = build_country_sources(
                    generated_country_sources=sources_for_country,
                    alpha2_code=random_country,
                    src_cat=random_category,
                )
                print(f'src_ids in sift_sources being sent to id_set_to_json = {src_ids}')
                json_payload = id_set_to_json(src_ids)
                print(f'payload being sent to send_payload in sift_sources ->')
                print(f'{json_payload}')
                send_payload(json_payload)
                return True
            else:
                print('returning false from sift sources')
                return False
        return False


def send_all_sources():
    print('top of all sources')
    if verify_base_categories() and verify_base_sources():
        print('inside verifies of send all sources')
        sources = Source.query.all()
        all_sources = {"sources": [source.json for source in sources]}
        try:
            print('about to send payload from send all sources -->')
            print(f'PAYLOAD = {all_sources}')

            if send_payload(all_sources):
                return True
        except ConnectionError:
            logger.log(
                level=logging.INFO, msg="Connection Error while delivering payload."
            )
    print('returning false from send all sources')
    return False


print("creating app")
app = create_app()
scheduler.add_job(id="send_all_src", func=send_all_sources)
scheduler.add_job(
    id="sifter_scheduler", func=sift_sources, trigger="interval", minutes=6
)
scheduler.start()
app.app_context().push()
from sifter.models import Source, Category


@app.shell_context_processor
def make_shell_context():
    return {"db": app.db, "Source": Source, "Category": Category}


@app.route("/stay_alive")
def stay_alive():
    logger.log(level=logging.INFO, msg="STAY ALIVE RECEIVED")
    print("STAYIN ALIVE")
    return json.dumps({"stay": "alive"}), 200, {"ContentType": "application/json"}


def id_set_to_json(id_set: set):
    json_payload = {"sources": [] for x in range(2)}
    print(f'initial payload = {json_payload} ')
    for src_id in id_set:
        source = Source.query.filter_by(id=src_id).first()
        print(f'source.json to add to payload = {source.json}')
        json_payload["sources"].append(source.json)
    print(f'payload returning from id_set_to_json = {json_payload}')
    return json_payload


def send_payload(payload: dict):
    print('PAYLOAD:')
    print(payload)
    login_url = os.getenv("NEWS_MAP_LOGIN_URL")
    username = os.getenv("NEWS_MAP_POST_USER")
    password = os.getenv("NEWS_MAP_POST_PW")
    post_url = os.getenv("NEWS_MAP_POST_URL")

    client = requests.session()
    client.get(login_url)
    csrf_token = client.cookies["csrftoken"]

    login_data = {
        "username": username,
        "password": password,
        "csrfmiddlewaretoken": csrf_token,
        "next": "/",
    }

    r1 = client.post(login_url, data=login_data, headers=dict(Referer=login_url))
    logger.log(level=logging.INFO, msg=f"response_1 => {r1}")
    print(f'r1 = {r1}')
    r2 = client.post(url=post_url, json=payload)
    logger.log(level=logging.INFO, msg=f"response_2 => {r2}")
    print(f'r2 = {r2}')
    # time.sleep(360)

    return True


def verify_base_categories():
    for category in categories:
        category = Category.query.filter_by(name=category).first()
        if not category:
            new_category = Category(name=category)
            db.session.add(new_category)
    db.session.commit()
    print('verified base categories')
    return True


def verify_base_sources():
    new_sources = set()
    first_source = Source.query.filter_by(id=1).first()
    if not first_source:
        try:
            with open("./static/js/top_sources.json") as json_data:
                source_data = json.load(json_data)["sources"]
                for source in source_data:
                    new_source_category = Category.query.filter_by(
                        name=source["category"]
                    ).first()
                    new_source = Source(
                        name=source["name"],
                        country=source["country"],
                        language=source["language"],
                        url=source["url"],
                        categories=[new_source_category],
                    )
                    db.session.add(new_source)
                    db.session.commit()
                    new_sources.add(new_source.id)
                json_payload = id_set_to_json(new_sources)
                print('verified base sources, about to send payload after building from file')
                if send_payload(json_payload):
                    print('sent payload after building base sources from file')
                    return True
            print('returning catch all false from verify base sources from file')
            return False

        except FileNotFoundError:
            logger.log(level=logging.INFO, msg="Error Building Base Sources from File")
            top_src_data = request_top_sources()
            if top_src_data:
                top_source_ids = build_top_sources(top_src_data)
                json_payload = id_set_to_json(top_source_ids)
                print('verified base sources via request, about to send payload')
                if send_payload(json_payload):
                    print('sent payload from verified base sources filenotfoundexception')
                    return True
            print('returning false inside filenotfounderror inside verified base sources')
            return False
    else:
        print('verified base sources already present in verified base sources')
        return True


def request_country_sources(alpha2_code, src_cat=None):

    key = os.getenv('NEWS_SRC_MS_API_KEY')
    print(f'key = {key}')
    print(f'alpha2_code = {alpha2_code}')
    print(f'src_cat = {src_cat}')
    if src_cat is None:
        endpoint = f"https://newsapi.org/v2/top-headlines?country={alpha2_code}&apiKey={key}"
    else:
        endpoint = f"https://newsapi.org/v2/top-headlines?country={alpha2_code}&category={src_cat}&apiKey={key}"
    print(f'endpoint = {endpoint}')
    response = requests.get(endpoint)
    print(f'CODE: {response.status_code}\nTEXT: {response.text}')
    print(f'\n\nRESPONSE = \n{response}\n\n')
    print(f'\n\nRESPONSE.json =\n{response.json}')

    if response.json()["status"] == "ok":
        data = response.json()["articles"]
        print('\n\nRESPONSE DATA[articles] =\n\n{data}')
        data_gen = (source for source in data)
        print('returning generated sources in request_country_sources')
        # return generated_sources(data_gen)
        return data

    elif response.json()["status"] == "error":
        logger.log(
            level=logging.ERROR,
            msg=f'Error Code: {response.json()["code"]} Message: {response.json()["message"]}',
        )
        print('returning none in request country sources')
        return None
    else:
        print('returning 2nd none in request country sources')
        return None


def build_country_sources(generated_country_sources, alpha2_code, src_cat):
    print('\n\nTOP OF BUILD_COUNTRY_SOURCES\n\n')
    new_and_updated_source_ids = set()
    category = Category.query.filter_by(name=src_cat).first()

    if category is None:
        category = Category(name=src_cat)
        db.session.add(category)
        db.session.commit()

    for src in generated_country_sources:
        print('top of "for src in generated_country_sources"')
        source = Source.query.filter_by(
            name=src["source"]["name"]
        ).first()  # check if source in db

        print(f'src from generator iteration in build_country_sources = {src}')

        if source is None:  # Source not in DB
            new_source = Source(
                name=src["source"]["name"],
                country=alpha2_code,
                language=country_codes.get(alpha2_code).get("language"),
            )
            new_source.categories.append(category)
            db.session.add(new_source)
            db.session.commit()
            print('adding new source to set in build country sources')
            print(f'new source being added = {new_source}')
            new_and_updated_source_ids.add(new_source.id)
            print(f'new_and_updated_source_ids after adding = {new_and_updated_source_ids}')

        else:  # Source already in DB
            print('source in build_country_sources already in db')
            try:
                idx = source.categories.index(
                    category
                )  # Check if category currently listed for source
            except ValueError:  # Exception Raised if category not listed
                source.categories.append(category)
                db.session.commit()
                print('addind source w new cat to set in build country sources')
                new_and_updated_source_ids.add(source.id)
    db.session.commit()
    print('finished building country sources')
    print(f'new_and_updated_source_ids in build_country_sources = {new_and_updated_source_ids}')
    print('\n\nBOTTOM OF BUILD_COUNTRY_SOURCES\n\n')
    return new_and_updated_source_ids


def request_top_sources():
    response = requests.get(f"https://newsapi.org/v2/sources?apiKey={api_key}")

    if response.json()["status"] == "ok":
        data = response.json()["sources"]
        top_sources_gen = (source for source in data)
        print('returning gen sources in request top sources')
        return generated_sources(top_sources_gen)

    elif response.json()["status"] == "error":
        logger.log(
            level=logging.ERROR,
            msg=f'Code: {response.json()["code"]}, Message: {response.json()["message"]}',
        )
        print('returning none in request top sources')
        return None


def build_top_sources(generated_top_sources):

    new_and_updated_id_set = (
        set()
    )  # Store ID of each new Source and Sources with a new Category.

    for src in generated_top_sources:
        print(f'source from gen_top_sources iteration in build_top_sources')
        category = Category.query.filter_by(
            name=src["category"]
        ).first()  # Check DB for Category[
        if category is None:  # Category does not exist in DB, add Category
            category = Category(name=src["category"])
            db.session.add(category)
            db.session.commit()

        source = Source.query.filter_by(
            name=src["name"]
        ).first()  # Checking DB for Source
        if source is None:  # Source does not exist in DB, add Source.
            source = Source(
                name=src["name"], country=src["country"], language=src["language"], url=src['url']
            )
            source.categories.append(category)
            db.session.add(source)
            db.session.commit()
            print(f'new_top_source_id for set == {source.id}')
            new_and_updated_id_set.add(source.id)
            print(f'after adding source.id, set = {new_and_updated_id_set}')
        else:  # Source exists in DB.
            print('source exists, checking category in build_top_sources')
            try:  # Check Source for Category
                idx = source.categories.index(category)
            except ValueError:  # Category does not exist for Source, add Category.
                source.categories.append(category)
                db.session.commit()
                print('adding already present source to nauis in build_top_sources')
                new_and_updated_id_set.add(source.id)

    db.session.commit()
    print('returning id set in build top sources')
    return new_and_updated_id_set


def generated_sources(src_gen):
    for src in src_gen:
        yield src
