# syntax=docker/Dockerfile:1
FROM python:3.11-slim-buster

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    lsb-release \
    software-properties-common

RUN wget -qO - https://packages.confluent.io/deb/7.3/archive.key | apt-key add -

# need to wait for [arm64 librdkafka-dev]
RUN add-apt-repository "deb [arch=amd64] https://packages.confluent.io/deb/7.3 stable main" && \
    add-apt-repository "deb https://packages.confluent.io/clients/deb $(lsb_release -cs) main"

RUN cat /etc/apt/sources.list

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    python3-dev \
    gcc \
    libc-dev \
    librdkafka-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -U -r /tmp/requirements.txt

COPY *.py ./
