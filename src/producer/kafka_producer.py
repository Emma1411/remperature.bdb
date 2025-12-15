from kafka import KafkaProducer
import json
import time
from src.sensor.temperature_sensor import TemperatureSensor

# Instanciation du producer Kafka
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # adresse de ton broker Kafka
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # sérialisation JSON
)

# Instanciation du capteur
sensor = TemperatureSensor()

# Nom du topic Kafka
topic = 'temperature_topic'

def send_temperature(interval=10):

    while True:
        # Lecture de la température
        value = sensor.read_value()
        data = {"temperature": value, "timestamp": time.time()}

        # Envoi de la valeur dans Kafka
        producer.send(topic, value=data)
        print(f"[Producer] Température envoyée : {value}°C")

        time.sleep(interval)  # pause entre chaque lecture

# Point d’entrée si on exécute ce fichier directement
if __name__ == "__main__":
    send_temperature()
