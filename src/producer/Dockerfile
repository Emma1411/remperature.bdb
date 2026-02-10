FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install kafka-python watchdog

ENV PYTHONPATH="/app"

CMD ["python", "src/producer/kafka_producer.py"]
