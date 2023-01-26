import requests
import datetime
import numpy as np
import pandas as pd
from lxml import html

from .db_tools import insert_many_data, read_data_from_col


header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
main_link = 'https://www.gismeteo.ru/diary/4368/{}/{}/'


def get_request(year: int, month: int, with_response: bool = False):
    response = requests.get(main_link.format(year, month), headers=header)
    code = html.fromstring(response.text)

    days = code.xpath("//tr//td[1]")
    day_weather = code.xpath("//tr//td[2]")
    evening_weather = code.xpath("//tr//td[7]")

    days = [int(item.text) for item in days]
    day_weather = [int(item.text) if item.text else np.nan for item in day_weather]
    evening_weather = [int(item.text) if item.text else np.nan for item in evening_weather]

    result = dict(zip(days, list(zip(day_weather, evening_weather))))

    if not with_response:
        return result
    else:
        return response, result


def prepare_parse_data(data: dict, today: pd.Timestamp) -> list:
    day_temp, evening_temp = data[today.day]

    day_date = pd.Timestamp(datetime.datetime(year=today.year, month=today.month, day=today.day, hour=10))
    evening_date = pd.Timestamp(datetime.datetime(year=today.year, month=today.month, day=today.day, hour=20))

    return [
        {'ds': day_date, 'y': day_temp},
        {'ds': evening_date, 'y': evening_temp}
    ]


def duplicate_data():
    data = read_data_from_col('history')[-2:]
    data[0]['ds'] += datetime.timedelta(days=1)
    data[1]['ds'] += datetime.timedelta(days=1)

    insert_many_data('history', data)


def last_day_parser(**kwargs):
    task_info = kwargs['task_instance']

    today = pd.Timestamp(datetime.date.today() - datetime.timedelta(days=1))
    print('Temperature parsing started for : ', today)

    data = get_request(today.year, today.month)
    
    if not today.day in data:
        if int(task_info.try_number) == 4:
            print('It was last try')
            print('Run duplicating last parse data')
            duplicate_data()
        else:
            print('failed to parse today temperature')
            raise Exception
    else:
        print('Data found')
        data = prepare_parse_data(data, today)
        insert_many_data('history', data)


if __name__ == "__main__":
    last_day_parser()
