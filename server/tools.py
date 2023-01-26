import datetime
import pymongo
import json
import pandas as pd

CONTENT_DIR = "static/content"


############### READ CONTENT FILES ###############
def read_json(name):
    with open(f"{CONTENT_DIR}/{name}.json", 'r') as f:
        obj = json.load(f)
    return obj


def read_html(name):
    with open(f"{CONTENT_DIR}/{name}.html", 'r') as f:
        obj = f.read()
    return obj


############### TRANSFORMATION OF DATES ###############
DICT_DAY_WEEK = {
    'Monday': 'Пн', 'Tuesday': 'Вт', 'Wednesday': 'Ср',
    'Thursday': 'Чт', 'Friday': 'Пт', 'Saturday': 'Сб', 'Sunday': 'Вс'
}

DICT_MONTHS = {
    'January': 'января', 'February': 'февраля', 'March': 'марта',
    'April': 'апреля', 'May': 'мая', 'June': 'июня', 'July': 'июля',
    'August': 'августа', 'September': 'сентября', 'October': 'октября',
    'November': 'ноября', 'December': 'декабря'
}

RU_MONTHS = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
             'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
NUM_TO_MONTH = dict(zip(range(1, 13), RU_MONTHS))


def transform_date(date):
    for word, replacement in DICT_MONTHS.items():
        date = date.replace(word, replacement)
    for word, replacement in DICT_DAY_WEEK.items():
        date = date.replace(word, replacement)
    return date


def get_today_date():
    return transform_date(datetime.date.today().strftime('%A, %d %B %Y'))


############### DATABASE TOOLS ###############
def get_col_from_db(col_name: str) -> pymongo.collection.Collection:
    # client = pymongo.MongoClient('mongodb://127.0.0.1:27017')
    client = pymongo.MongoClient('mongodb://database')
    db = client["weather"]

    return db[col_name]


def insert_many_data(col_name: str, data: list, drop_table=False):
    col = get_col_from_db(col_name)
    if drop_table:
        col.drop()
    col.insert_many(data)


def read_data_from_col(col_name: str) -> list:
    col = get_col_from_db(col_name)

    return list(col.find({}, {'_id': False}))


############### FOR HISTORY PAGE ###############
def get_history_weather(month, year):
    df = pd.DataFrame(read_data_from_col('history'))

    tmp = df[(pd.to_datetime(df['ds']).dt.month == month) &
             (pd.to_datetime(df['ds']).dt.year == year)]
    day_temp = list(tmp.loc[pd.to_datetime(tmp['ds']).dt.hour == 10, 'y'])
    evening_temp = list(tmp.loc[pd.to_datetime(tmp['ds']).dt.hour == 20, 'y'])
    days = list(range(1, len(day_temp) + 1))
    data = pd.DataFrame({'num': days, 'day_temp': day_temp, 'evening_temp': evening_temp})
    return data.to_dict(orient='records')
