from kafka import KafkaConsumer
import json

# Création du consumer
consumer = KafkaConsumer(
    'temperature_topic',               # Le topic à écouter
    bootstrap_servers='localhost:9092',# Adresse du broker Kafka
    auto_offset_reset='earliest',      # Commence à lire depuis le début
    group_id='temperature_group',      # Nom du groupe de consommateurs
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))  # Désérialisation JSON
)

print("[Consumer] En attente de messages... Ctrl+C pour quitter")

# Boucle infinie pour recevoir les messages
for message in consumer:
    print(f"[Consumer] Température reçue : {message.value['temperature']}°C à timestamp {message.value['timestamp']}")
