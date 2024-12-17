FROM python:alpine3.17

WORKDIR /app

COPY ./Entities /app/Entities
COPY ./Core /app/Core

COPY ./CapitalGainsService/CapitalGainsService.py /app/CapitalGainsService.py
COPY ./CapitalGainsService/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=CapitalGainsService.py

CMD ["python", "CapitalGainsService.py"]