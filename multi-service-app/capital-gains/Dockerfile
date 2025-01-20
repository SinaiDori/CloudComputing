FROM python:alpine3.17

WORKDIR /app

COPY ./entities /app/entities
COPY ./core /app/core

COPY ./capital-gains/CapitalGainsService.py /app/CapitalGainsService.py
COPY ./capital-gains/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=CapitalGainsService.py

CMD ["python", "CapitalGainsService.py"]