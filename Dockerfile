FROM python:3
LABEL maintainer="zhukov9523@gmail.com"

ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y libgeos-dev libproj-dev gdal-bin

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
