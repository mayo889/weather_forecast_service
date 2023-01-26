import datetime
import pandas as pd
from os import path 
from prophet.serialize import model_from_json, model_to_json

from .db_tools import read_data_from_col, insert_many_data
from .paths import MODEL_FILENAME, MODEL_PATH


pd.options.mode.chained_assignment = None


def get_dates_to_predict(last_date, num_days=7):
    dates_to_predict = []
    for days in range(1, 1 + num_days):
        cur_date = last_date +  datetime.timedelta(days=days)
        dates_to_predict.append(cur_date.replace(hour=10))
        dates_to_predict.append(cur_date.replace(hour=20))
        
    return pd.DataFrame(dates_to_predict, columns=['ds'])


def get_preds(df, model):
    last_date = df.iloc[-1]['ds']

    dates_to_predict = get_dates_to_predict(last_date)

    forecast = model.predict(dates_to_predict)
    
    preds_df = forecast[['ds', 'yhat']]
    preds_df['yhat'] = preds_df['yhat'].round().astype('int')

    return preds_df


def save_preds(preds_df):
    data = preds_df.to_dict(orient='records')

    insert_many_data('predictions_7days', data, drop_table=True)
    insert_many_data('predictions', data[:2])


def predict_and_save(): 
    with open(path.join(MODEL_PATH, MODEL_FILENAME), 'r') as fin:
        saved_model = model_from_json(fin.read())

    df = pd.DataFrame(read_data_from_col('history'))

    preds_df = get_preds(df, saved_model)

    save_preds(preds_df)
