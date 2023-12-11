# syntax=docker/dockerfile:1
FROM python:3.10.9
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN apt-get update -y
RUN apt-get install ffmpeg -y
RUN apt-get install -y imagemagick
RUN DEBIAN_FRONTEND="noninteractive" apt-get install libmagickwand-dev --no-install-recommends -y
COPY . /code/