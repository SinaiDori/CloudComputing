FROM python:alpine3.17

WORKDIR /app

COPY app.py /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

ENV FLASK_APP=app.py
ENV FLASK_RUN_PORT=5001

CMD ["flask", "run", "--host=0.0.0.0"]