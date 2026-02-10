from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    "temperature_topic",
    bootstrap_servers="kafka:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="temperature-group",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    api_version=(3, 5, 0),          # ← même chose ici
)

if __name__ == "__main__":
    print("[Consumer] En attente de messages...")

    for message in consumer:
        print("[Consumer] Message reçu :", message.value)
