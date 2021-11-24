FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update -y
RUN apt-get install -y python3-pip

ADD . /ICT3102_Proj_old
WORKDIR /ICT3102_Proj_old

COPY ./requirements.txt ./requirements.txt

RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt