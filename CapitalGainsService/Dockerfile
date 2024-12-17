FROM python:alpine3.17

WORKDIR /app

COPY CapitalGainsService.py /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5003

ENV FLASK_APP=CapitalGainsService.py
ENV FLASK_RUN_PORT=5003

CMD ["flask", "run", "--host=0.0.0.0"]