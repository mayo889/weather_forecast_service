import pymongo
import pandas as pd

from pipeline.dags.operators.db_tools import insert_many_data, read_data_from_col, get_col_from_db


def test_get_collection_from_db():
    col = get_col_from_db('history')

    assert isinstance(col, pymongo.collection.Collection)


def test_write_and_read():
    data_df = pd.DataFrame(range(10), columns=['y'])
    data = data_df.to_dict(orient='records')
    write_data = data_df.to_dict(orient='records')

    insert_many_data('tests', write_data)
    read_data = read_data_from_col('tests')

    assert data == read_data, "read data is not equal to written data"
