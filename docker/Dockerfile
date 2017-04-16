FROM python:3.6-alpine
ADD . /code
WORKDIR /code
RUN apk add --update make gcc g++ coreutils
RUN pip install --no-cache-dir -r requirements.txt
