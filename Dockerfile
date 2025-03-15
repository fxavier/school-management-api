FROM python:3.13.2-alpine3.21
LABEL maintainer="Xavier Nhagumbe"

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt  /requirements.txt
COPY ./app /app

WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \ 
    #    gcc libc-dev linux-headers postgresql-dev && \
    /py/bin/pip install -r /requirements.txt && \
    apk del .tmp-build-deps && \
    adduser --disabled-password --no-create-home app 


ENV PATH="/py/bin:$PATH"

USER app