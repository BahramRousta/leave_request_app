FROM python

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./web /app

WORKDIR /app

COPY ./requirements.txt requirements.txt

RUN pip install -r requirements.txt
