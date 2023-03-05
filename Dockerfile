FROM python:3.8-slim-buster

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./web /web

WORKDIR /web

COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt
