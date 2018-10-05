FROM ubuntu:18.04

RUN apt-get update -y \
  && apt-get install -y python3.7 python3-dev python3-setuptools python3-pip apt-utils \
  && apt-get install -y postgresql-client libxml2-dev libxslt-dev git \
  && apt-get install -y alien libaio1 && apt-get clean

COPY ./oracle_instant_client /oracle_instant_client

WORKDIR /oracle_instant_client
RUN python3 install_oracle_instantclient.py ./


RUN rm -fr /oracle_instant_client

COPY . /app

WORKDIR /app
RUN python3 -m pip install -r requirements.txt
RUN python3 setup.py install

WORKDIR /
RUN rm -fr /app

USER 10000
