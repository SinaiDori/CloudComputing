FROM python:alpine3.17

WORKDIR /app

COPY MongoDBService.py /app
COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 27017

ENV FLASK_APP=MongoDBService.py
ENV MONGO_DB_CONTAINER_PORT=27017

CMD ["flask", "run", "--host=0.0.0.0"]