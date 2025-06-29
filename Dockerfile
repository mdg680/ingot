FROM python:3.13-alpine
LABEL authors="Peter Rønholt"

RUN apk add --no-cache git

RUN python -m pip install --upgrade pip

COPY . .

RUN python -m pip install -e .