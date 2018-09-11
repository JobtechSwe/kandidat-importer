FROM ubuntu:18.04

COPY . /app
COPY ./oracle_instant_client /oracle_instant_client

RUN apt-get update -y \
  && apt-get install -y python3.7 python3-dev python3-setuptools apt-utils \
  && apt-get install -y postgresql-client libxml2-dev libxslt-dev \
  && apt-get install -y alien libaio1 


WORKDIR /oracle_instant_client
RUN python3 install_oracle_instantclient.py ./
#RUN alien -iv oracle-instantclient18.3-basic-18.3.0.0.0-1.x86_64.rpm 
#RUN alien -iv oracle-instantclient18.3-devel-18.3.0.0.0-1.x86_64.rpm 
#RUN alien -iv oracle-instantclient18.3-sqlplus-18.3.0.0.0-1.x86_64.rpm 

#ENV ORACLE_HOME=/usr/lib//oracle/18.3/client64

WORKDIR /app
RUN python3 setup.py install

WORKDIR /
# RUN rm -fr /app
RUN apt-get clean

