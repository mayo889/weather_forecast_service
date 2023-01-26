import pytest
import os
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_int64_dtype
from prophet import Prophet

from pipeline.dags.operators.predict import get_dates_to_predict, get_preds, save_preds
from pipeline.dags.operators.db_tools import read_data_from_col
from pipeline.dags.operators import content

content.CONTENT_DIR = "tests/content"


@pytest.mark.parametrize(
    "last_date, num_days, expected",
    [(
        pd.Timestamp(year=2023, month=1, day=1), 1,
        pd.DataFrame([pd.Timestamp(year=2023, month=1, day=2, hour=10),
                      pd.Timestamp(year=2023, month=1, day=2, hour=20)],
                     columns=['ds'])
    )]
)
def test_get_dates_to_predict(last_date, num_days, expected):
    dates_to_predict = get_dates_to_predict(last_date, num_days)

    assert expected.equals(dates_to_predict), "incorrect function output"


def fit_model():
    df = pd.DataFrame(data={
        'ds': [pd.Timestamp(year=2023, month=1, day=1, hour=10),
               pd.Timestamp(year=2023, month=1, day=1, hour=20)],
        'y': [10, 15]
    })
    model = Prophet()
    model.fit(df)
    
    return df, model


def test_predictions():
    df, model = fit_model()

    preds = get_preds(df, model)
    assert preds.shape == (7 * 2, 2), "wrong dimensions of predictions df"
    assert is_datetime64_any_dtype(preds['ds']), "wrong type of ds column"
    assert is_int64_dtype(preds['yhat']), "wrong type of yhat column"

    save_preds(preds)
    read_preds = pd.DataFrame(read_data_from_col('predictions_7days'))
    assert preds.equals(read_preds), "read preds is not equal to written preds"

    content.transform_preds()
    assert os.path.exists(f"{content.CONTENT_DIR}/preds.json"), "file with predictions was not created"
