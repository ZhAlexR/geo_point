# syntax=docker/dockerfile:1
FROM python:3
LABEL maintainer="zhukov9523@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
