import pandas as pd
import pymongo


DATA_FOLDER = 'data'
# DATABASE_URL = 'mongodb://127.0.0.1:27017'
DATABASE_URL = 'mongodb://database'

def get_col_from_db(col_name):
    client = pymongo.MongoClient(DATABASE_URL)
    db = client["weather"]
    return db[col_name]


def clear_db():
    client = pymongo.MongoClient(DATABASE_URL)
    client.drop_database('weather')


def fill_from_csv_to_bd(csv_name):
    df = pd.read_csv(f"{DATA_FOLDER}/{csv_name}.csv", parse_dates=['ds'])
    data = df.to_dict(orient='records')
    col = get_col_from_db(csv_name)
    col.insert_many(data)


def prefill_all_data():
    fill_from_csv_to_bd('history')
    fill_from_csv_to_bd('predictions')
    fill_from_csv_to_bd('metrics')


if __name__ == "__main__":
    clear_db()
    prefill_all_data()
