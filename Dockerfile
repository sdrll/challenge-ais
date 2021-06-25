# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster

RUN apt-get update && apt-get -y install libspatialindex-dev

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install -r requirements.txt

COPY . /opt/app

CMD [ "python", "/opt/app/main.py" ]