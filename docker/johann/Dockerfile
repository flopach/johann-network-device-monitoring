# CISCO SAMPLE CODE LICENSE
# Version 1.1
# Copyright (c) 2021 Cisco and/or its affiliates

# Dockerfile for johann Django app

FROM python:3.9-slim

RUN mkdir -p /opt/johann/
COPY . /opt/johann/

WORKDIR /opt/johann

RUN mkdir -p ./stickydata

ENV PYTHONUNBUFFERED=0
ENV SECRET_KEY=cFRXsdHd2K20lRewWXV5vjbxOWousmGE
ENV DJANGO_SETTINGS_MODULE=johann.settings_production
ENV DJANGO_SUPERUSER_EMAIL=admin@cisco.com
ENV DJANGO_SUPERUSER_USERNAME=admin
ENV DJANGO_SUPERUSER_PASSWORD=admin123

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod +x ./start_johann.sh
CMD ./start_johann.sh

EXPOSE 8000