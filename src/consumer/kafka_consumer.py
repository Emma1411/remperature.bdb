import json

from kafka import KafkaConsumer


def load_data():
    consumer = KafkaConsumer('TEMPERATURE_CAPTEUR', bootstrap_servers='localhost:9092',
                             value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    for message in consumer:
        print('recu',message.value)
