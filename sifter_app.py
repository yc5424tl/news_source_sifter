from sifter import create_app, scheduler, db
import os


import time
import json
import random
import requests
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
    "dj": "Djibout   i",
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
    print('top of sifter')
    with app.app_context():
        print('with context')
        if send_all_sources():
            print('sent all sources')
            countries = list(api_country_codes.keys())
            random_country = random.choice(countries)
            random_category = random.choice(categories)
            sources_for_country = req_country_src_data(
                alpha2_code=random_country, src_cat=random_category
            )
            if sources_for_country():
                print('have sources for country')
                src_update = build_country_src_data(
                    src_data=sources_for_country,
                    alpha2_code=random_country,
                    src_cat=random_category,
                )
                print(f'\n\n==============SIFTER PAYLOAD===============\n\n{src_update}')
                if send_payload(src_update):
                    print('sifter payload delivered')
                else:
                    print('NOT sifter payload delivered')
            else:
                print('NOT sources_for_country')
        else:
            print('NOT sent all sources')


print("MAIN - creating app")
app = create_app()
scheduler.add_job(
    id="sifter_scheduler", func=sift_sources, trigger="interval", minutes=1, max_instances=1, replace_existing=True
)
scheduler.start()
print('MAIN - started scheduler')
logger.log(level=logging.INFO, msg='started scheduler')
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


def send_payload(payload: set):
    print('top send_payload')
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
    payload = {'sources': frozenset(payload)}
    print("\n\n============PAYLOAD================")
    print(f'{payload}')
    print('===========END PAYLOAD=============\n\n')
    try:
        r1 = client.post(login_url, data=login_data, headers=dict(Referer=login_url))
        logger.log(level=logging.INFO, msg=f"response_1 => {r1}")
        print(f'r1 @ send_payload == {r1}')
        r2 = client.post(url=post_url, json=payload)
        logger.log(level=logging.INFO, msg=f"response_2 => {r2}")
        print(f'r2 @ send_payload == {r2}')
        print('bottom send_payload -- success')
        return True
    except ConnectionError:
        logger.log(
            level=logging.INFO, msg="Connection Error while delivering payload."
        )
        print('bottom send_payload -- exception failure')
        return False


def send_all_sources():
    print('top send_all_sources')
    if verify_base_cat() and verify_base_src():
        print('verify_base_cat() and verify_base_src() @ send_all_sources')
        print(Source.query.all().count())
        sources = Source.query.all()
        src_update = set()
        for src in sources:
            print(f'src.json for src_update.add(src.json) == {src.json}')
            src_update.add(src.json)

        # all_src_update = set(src.json for src in sources)
        print('pre-payload @ send_all_sources')
        if send_payload(src_update):
            print('bottom send_all_sources -- success @ send_payload')
            return True
        else:
            print('bottom send_all_sources -- failure @ send_payload')
            return False
    else:
        print('bottom send_all_sources -- failure @ verify_base_cat and verify_base_src')
        return False


def verify_base_cat():
    print('top verify_base_cat')
    for cat in categories:
        cat = Category.query.filter_by(name=cat).first()
        if not cat:
            new_cat = Category(name=cat)
            db.session.add(new_cat)
    db.session.commit()
    print('bottom verify_base_cat -- success')
    return True


def verify_base_src():
    print('top verify_base_src')
    first_src = Source.query.filter_by(id=1).first()
    if not first_src:
        src_update = set()
        try:
            with open("./static/js/top_sources.json") as json_data:
                src_data = json.load(json_data)["sources"]
                for src in src_data:
                    new_src_cat = Category.query.filter_by(
                        name=src["category"]
                    ).first()
                    new_source = Source(
                        name=src["name"],
                        country=src["country"],
                        language=src["language"],
                        url=src["url"],
                        categories=[new_src_cat],
                    )
                    db.session.add(new_source)
                    db.session.commit()
                    src_update.add(new_source.json)
                print('pre-payload verify_base_src-file')
                if send_payload(src_update):
                    print('bottom verify_base_src-file -- success')
                    return True
            print('bottom verify_base_sec-file -- failure')
            logger.log(level=logging.INFO, msg='Error sending payload from file in verify_base_src()')
            return False
        except FileNotFoundError:
            logger.log(level=logging.INFO, msg="Unable to locate file in verify_base_src()")
            src_data = req_top_src_data()
            if src_data:
                src_update = build_top_src_data(src_data)
                print('pre-payload verify_base_src-req')
                if send_payload(src_update):
                    print('bottom verify_base_src-req -- success')
                    scheduler.pause()
                    print('paused scheduler, waiting six minutes')
                    time.sleep(360)
                    scheduler.resume()
                    print('resumed scheduler')
                    return True
            logger.log(level=logging.INFO, msg='No data returned from req_top_src_data in verify_base_src')
            print('bottom verify_base_src-req -- failure')
            return False
    else:
        print('bottom verify_base_src-no_update_needed -- success')
        return True


def req_country_src_data(alpha2_code, src_cat=None):
    print('top of req_country_src_data')
    if src_cat is None:
        endpoint = f"https://newsapi.org/v2/top-headlines?country={alpha2_code}&apiKey={api_key}"
    else:
        endpoint = f"https://newsapi.org/v2/top-headlines?country={alpha2_code}&category={src_cat}&apiKey={api_key}"
    response = requests.get(endpoint)
    if response.json()["status"] == "ok":
        print('bottom req_country_src_data -- success')
        return response.json()["articles"]
    elif response.json()["status"] == "error":
        print('bottom req_country_src_data -- failure')
        logger.log(
            level=logging.ERROR,
            msg=f'Error Code: {response.json()["code"]} Message: {response.json()["message"]}',
        )
        return None


def build_country_src_data(src_data, alpha2_code, src_cat):
    print('top build_country_src_data')
    src_update = set()
    cat = Category.query.filter_by(name=src_cat).first()
    if cat is None:
        cat = Category(name=src_cat)
        db.session.add(cat)
        db.session.commit()
        print('added category in build_country_src_data -- new_category')
    for art in src_data:
        src = Source.query.filter_by(
            name=art["source"]["name"]
        ).first()  # check if source in db
        if src is None:  # Source not in DB
            new_src = Source(
                name=art["source"]["name"],
                country=alpha2_code,
                language=country_codes.get(alpha2_code).get("language"),
            )
            new_src.categories.append(cat)
            db.session.add(new_src)
            db.session.commit()
            src_update.add(new_src.json)
            print('added src to list in build_country_src_data -- new_src')
        else:  # Source already in DB
            try:
                idx = src.categories.index(cat)  # Check if category currently listed for source
                print('src and src.cat current @ build_country_src_data')
            except ValueError:  # Exception Raised if category not listed
                src.categories.append(cat)
                db.session.commit()
                src_update.add(src.json)
                print('added src to list in build_country_src_data -- updated_cat')
    db.session.commit()
    print('bottom build_country_src_data -- success')
    return src_update


def req_top_src_data():
    print('top req_top_src_data')
    response = requests.get(f"https://newsapi.org/v2/sources?apiKey={api_key}")
    if response.json()["status"] == "ok":
        print('bottom req_top_src_data -- success')
        return response.json()["sources"]
    elif response.json()["status"] == "error":
        logger.log(
            level=logging.ERROR,
            msg=f'Code: {response.json()["code"]}, Message: {response.json()["message"]}',
        )
        print('bottom req_top_src_data -- failure')
        return None


def build_top_src_data(src_data):
    print('top build_top_src_data')
    src_update = set()
    for src in src_data:
        cat = Category.query.filter_by(
            name=src["category"]
        ).first()  # Check DB for Category[
        if cat is None:  # Category does not exist in DB, add Category
            cat = Category(name=src["category"])
            db.session.add(cat)
            db.session.commit()
            print('added cat in build_top_src_data -- new_cat')
        src = Source.query.filter_by(
            name=src["name"]
        ).first()  # Checking DB for Source
        if src is None:  # Source does not exist in DB, add Source.
            new_src = Source(
                name=src["name"], country=src["country"], language=src["language"], url=src['url']
            )
            new_src.categories.append(cat)
            db.session.add(new_src)
            db.session.commit()
            src_update.add(new_src.json)
            print('added new_src to list in build_top_src_data')
        else:  # Source exists in DB.
            try:  # Check Source for Category
                idx = src.categories.index(cat)
                print('src and src.cat is current @ build_top_src_data')
            except ValueError:  # Category does not exist for Source, add Category.
                src.categories.append(cat)
                db.session.commit()
                src_update.add(src.json)
                print('updated src with new cat in build_top_src_data')
    db.session.commit()
    print('bottom build_top_src_data -- success')
    return src_update

