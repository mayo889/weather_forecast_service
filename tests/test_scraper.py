import datetime
import pytest
import pandas as pd

from pipeline.dags.operators.everyday_parser import get_request, prepare_parse_data


def test_scraper():
    today = pd.Timestamp(datetime.date.today())

    response, data = get_request(today.year, today.month, with_response=True)

    assert response.status_code == 200, "request failed"
    assert len(data) > 0, "empty data from request"


@pytest.mark.parametrize(
    "test_input, expected",
    [(
        ({1: [10, 15]}, pd.Timestamp(year=2023, month=1, day=1)),
        [{'ds': pd.Timestamp(year=2023, month=1, day=1, hour=10), 'y': 10},
         {'ds': pd.Timestamp(year=2023, month=1, day=1, hour=20), 'y': 15}]
    )]
)
def test_preparing_parse_data(test_input, expected):
    data, today = test_input
    prepared_data = prepare_parse_data(data, today)

    assert expected == prepared_data, "incorrect function output"


if __name__ == "__main__":
    test_scraper()
