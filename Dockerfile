# syntax=docker/dockerfile:1
FROM alpine:latest

RUN apk update && apk add python3-dev && apk add py3-pip

RUN mkdir /top_crypto_price_list
WORKDIR /top_crypto_price_list

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app .

RUN adduser -D crypto
USER crypto
