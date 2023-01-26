import pymongo
import os
import pandas as pd
from .paths import BACKUP_DIR

# DATABASE_URL = 'mongodb://127.0.0.1:27017'
DATABASE_URL = 'mongodb://database'


def clear_db():
    client = pymongo.MongoClient(DATABASE_URL)
    client.drop_database('weather')


def get_col_from_db(col_name: str) -> pymongo.collection.Collection:
    client = pymongo.MongoClient(DATABASE_URL)
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


def make_data_backup():
    for col_name in ['history', 'metrics', 'predictions']:
        os.remove(f'{BACKUP_DIR}/{col_name}.csv')
        data = pd.DataFrame(read_data_from_col(col_name))
        data.to_csv(f'{BACKUP_DIR}/{col_name}.csv', index=False)
