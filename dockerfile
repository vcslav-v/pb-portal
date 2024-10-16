FROM python:3.11-slim

RUN apt-get update && apt-get install -y git

RUN mkdir -p /usr/src/app/admin_bot

ENV CONTAINER_HOME=/usr/src/app/pb_portal

ADD . $CONTAINER_HOME
WORKDIR $CONTAINER_HOME

RUN pip install --upgrade pip
RUN pip install -r requirements.txt