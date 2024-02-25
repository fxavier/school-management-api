FROM python:3.12-alpine
LABEL maintainer="Xavier Nhagumbe"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt  /requirements.txt
COPY ./app /app

WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
  #  apk add --update --no-cache postgresql-client && \
  #  apk add --update --no-cache --virtual .tmp-build-deps \
  #      gcc libc-dev linux-headers postgresql-dev && \
    /py/bin/pip install -r /requirements.txt && \
    adduser --disabled-password --no-create-home app 
   # apk del .tmp-build-deps

ENV PATH="/py/bin:$PATH"

USER app