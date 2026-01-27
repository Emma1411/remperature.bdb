from kafka import KafkaProducer
import json
import time
from src.loader.csv_loader import watch_for_new_files

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def format_message(entry):
    return {
        "timestamp": entry["date"],
        "temperature": entry
    }

if __name__ == "__main__":
    print("[Producer] Surveillance du dossier temp/data...")

    for new_data in watch_for_new_files():
        print(f"[Producer] Nouveau fichier détecté ({len(new_data)} lignes)")

        for entry in new_data:
            message = format_message(entry)
            producer.send("temperature_topic", message)
            print("[Producer] envoyé :", message)
            time.sleep(1)

        producer.flush()
