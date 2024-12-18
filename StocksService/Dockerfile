FROM python:alpine3.17

WORKDIR /app

COPY ./Entities /app/Entities
COPY ./Core /app/Core
COPY ./MongoDBService /app/MongoDBService

COPY ./StocksService/StocksService.py /app/StocksService.py
COPY ./StocksService/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=StocksService.py
CMD ["python", "StocksService.py"]