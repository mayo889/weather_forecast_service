FROM python:3.8

ADD requirements.txt /opt/app/requirements.txt
RUN pip install -r /opt/app/requirements.txt

RUN mkdir -p ./opt/models

RUN pip install "apache-airflow[celery]==2.5.0" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.5.0/constraints-3.8.txt"

ADD ./dags /root/airflow/dags/

RUN rm /usr/local/lib/python3.8/site-packages/airflow/example_dags/*.py

RUN airflow db init
RUN airflow users create --role Admin --username dmls --email dmls --firstname dmls --lastname dmls --password dmls
