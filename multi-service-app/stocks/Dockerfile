FROM python:alpine3.17

WORKDIR /app

COPY ./entities /app/entities
COPY ./core /app/core
COPY ./mongo /app/mongo
COPY ./StocksService.py /app/StocksService.py
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=StocksService.py
CMD ["python", "StocksService.py"]