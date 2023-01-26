import requests
import datetime
import numpy as np
import pandas as pd
from lxml import html
from tqdm import tqdm


header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
main_link = 'https://www.gismeteo.ru/diary/4368/{}/{}/'
data = np.empty((0, 5))


def get_request(year, month):
    response = requests.get(main_link.format(year, month), headers=header)
    code = html.fromstring(response.text)

    days = code.xpath("//tr//td[1]")
    day_weather = code.xpath("//tr//td[2]")
    evening_weather = code.xpath("//tr//td[7]")

    days = [int(item.text) for item in days]
    day_weather = [int(item.text) if item.text else np.nan for item in day_weather]
    evening_weather = [int(item.text) if item.text else np.nan for item in evening_weather]

    transform_data(year, month, days, day_weather, evening_weather)
    

def transform_data(year, month, days, day_weather, evening_weather):
    global data

    # В исторических данных есть дни, по которым не известна погода,
    # Добавим эти дни к общим данным.
    cur_data = dict(zip(days, list(zip(day_weather, evening_weather))))
    days_in_month = pd.Period(f'{year}-{month}-01').days_in_month
    new_data = []
    for day in range(1, days_in_month + 1):
        if day in cur_data:
            new_data.append([day] + list(cur_data[day]))
        else:
            new_data.append([day, np.nan, np.nan])
    new_data = np.array(new_data)

    # Преобразуем в удобный построчный формат для сохранения
    weather = np.array(list(zip(new_data[:, 1], new_data[:, 2]))).flatten()
    days = new_data[:, 0]

    len_month = len(days) * 2

    month_weather = np.stack((
        np.repeat(year, len_month),
        np.repeat(month, len_month),
        np.repeat(days, 2),
        # np.resize(['afternoon', 'evening'], len_month)
        np.resize([10, 20], len_month),
        weather.flatten()
    ), axis=1)

    data = np.vstack((data, month_weather))


def final_transform(data):
    today = pd.Timestamp(datetime.date.today())

    df = pd.DataFrame(data,
                      columns=['year', 'month', 'day', 'hour', 'temp'])
    df['date'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df = df[['date', 'temp']]

    df = df.loc[df['date'] < today]

    # заполнение пропусков
    df['temp'].interpolate(inplace=True)
    df['temp'] = df['temp'].astype('int')

    df.columns = ['ds', 'y']

    return df


def parser():
    global data
    today = datetime.date.today()
    list_years = list(range(2000, today.year))
    list_months = list(range(1, 13))

    for year in tqdm(list_years):
        for month in tqdm(list_months, leave=False):
            get_request(year, month)

    # отдельный проход по месяцам текущего года
    for month in tqdm(list(range(1, today.month + 1))):
        get_request(today.year, month)

    df = final_transform(data)
    
    df.to_csv("weather_data.csv", index=False)


if __name__ == "__main__":
    parser()
