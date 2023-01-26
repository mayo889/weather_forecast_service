FROM python:3.8

ADD requirements.txt /opt/app/requirements.txt
RUN pip install -r /opt/app/requirements.txt

ADD . /scripts

WORKDIR /scripts

EXPOSE 8000
