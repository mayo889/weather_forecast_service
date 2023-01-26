import json
import pandas as pd
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn import metrics

from .db_tools import read_data_from_col, insert_many_data
from .paths import CONTENT_DIR


############### TRANSFORMATION OF PREDICTIONS ###############
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


def transform_date(date):
    for word, replacement in DICT_MONTHS.items():
        date = date.replace(word, replacement)
    for word, replacement in DICT_DAY_WEEK.items():
        date = date.replace(word, replacement)
    return date


def transform_preds():
    data = read_data_from_col('predictions_7days')
    preds = []

    for i in range(0, len(data), 2):
        day = data[i]
        evening = data[i+1]

        date = day['ds'].strftime('%A, %d %B')
        
        preds.append(
            dict(
                date = transform_date(date),
                day_temp = round(day['yhat']),
                evening_temp = round(evening['yhat'])
            )
        )

    with open(f"{CONTENT_DIR}/preds.json", 'w', encoding='utf-8') as f:
        json.dump(preds, f, ensure_ascii=False, indent=4)


############### FOR GRAPHING ###############
def get_preds_and_true():
    preds = pd.DataFrame(read_data_from_col('predictions')[:-2])
    true = pd.DataFrame(read_data_from_col('history')[-len(preds):])

    assert preds.shape == true.shape
    assert preds.loc[0, 'ds'] == preds.loc[0, 'ds']
    assert preds.loc[len(preds)-1, 'ds'] == preds.loc[len(preds)-1, 'ds']

    return true.merge(preds, on='ds')


############### GRAPH PREDICTIONS ###############
def graph_predictions():
    df = get_preds_and_true()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['ds'], y=df['y'],
                            mode="lines+markers",
                            name='true temp'))
    fig.add_trace(go.Scatter(x=df['ds'], y=df['yhat'],
                            mode="lines+markers",
                            name='predict temp'))
    plotly.io.write_html(fig, f"{CONTENT_DIR}/graph.html")


############### GRAPH METRICS ###############
def calc_metrics():
    df = get_preds_and_true()
    
    mae = metrics.mean_absolute_error(df['y'], df['yhat'])
    mse = metrics.mean_squared_error(df['y'], df['yhat'], squared=True)
    rmse = metrics.mean_squared_error(df['y'], df['yhat'], squared=False)

    data = [{
        'ds': df.iloc[-1]['ds'].strftime("%Y-%m-%d"),
        'mae': round(mae, 2),
        'mse': round(mse, 2),
        'rmse': round(rmse, 2)
    }]
    
    insert_many_data('metrics', data)


def graph_metrics():
    calc_metrics()
    df = pd.DataFrame(read_data_from_col('metrics'))

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df['ds'], y=df['mae'],
                            mode="lines+markers",
                            name='mae'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['ds'], y=df['rmse'],
                            mode="lines+markers",
                            name='rmse'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['ds'], y=df['mse'],
                            mode="lines+markers",
                            name='mse'), secondary_y=True)
    fig.update_yaxes(title_text="<b>mae/rmse</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>mse</b>", secondary_y=True)
    plotly.io.write_html(fig, f"{CONTENT_DIR}/metrics.html")


if __name__ == "__main__":
    transform_preds()
    graph_predictions()
    graph_metrics()
