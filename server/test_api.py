import pytest
import json

import tools
from server import app

tools.CONTENT_DIR = "tests/content"


def test_api_predictions_route():
    response = app.test_client().get('/api/predictions')
    assert response.status_code == 200, "wrong status_code"

    res = json.loads(response.data.decode('utf-8'))
    preds = list(res.values())

    assert len(preds) == 7, "the number of predictions is not equal to 7"
    for pred in preds:
        assert set(pred.keys()) == set(['date', 'day_temp', 'evening_temp']), "predictions have wrong fields"
    
    pred = preds[0]
    assert isinstance(pred['date'], str), "wrong type of date"
    assert isinstance(pred['day_temp'], int), "wrong type of day temperature"
    assert isinstance(pred['evening_temp'], int), "wrong type of evening temperature"


@pytest.mark.parametrize(
    "day, date",
    [
        (1, 'Пн, 02 января'),
        (7, 'Вс, 08 января'),
        pytest.param(8, 'Пн, 09 января', marks=pytest.mark.xfail)
    ]
)
def test_api_predictions_day_route(day, date):
    response = app.test_client().get(f'/api/predictions/{day}')
    assert response.status_code == 200, "wrong status_code"

    res = json.loads(response.data.decode('utf-8'))

    assert res['date'] == date, "wrong date from api"
    assert isinstance(res['day_temp'], int)
    assert isinstance(res['evening_temp'], int)
