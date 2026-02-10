FROM python:3.10

WORKDIR /app

COPY src/consumer/ /app/

RUN pip install kafka-python

CMD ["python", "kafka_consumer.py"]