from kafka import KafkaProducer
import json
from src.loader.csv_loader import load_temperatures


def write_data():
    producer = KafkaProducer(bootstrap_servers='localhost:9092',
    value_serializer = lambda x: json.dumps(x).encode('utf-8')
                             )
    TOPIC = 'TEMPERATURE_CAPTEUR'
    while True:
         for line in load_temperatures.data:
           message = line.strip()
           producer.send(TOPIC, line)
           print(f"envoyer -{message}")
           producer.flush()
           producer.close()
