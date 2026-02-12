import os
import glob
import json
import sys
sys.path.append("/opt/airflow")

from kafka import KafkaProducer
from src.loader.csv_loader import read_csv_file

TOPIC = "temperature_topic"
DATA_DIR = "/opt/airflow/temp/data"

producer = KafkaProducer(
    bootstrap_servers="kafka:29092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    retries=5,
    request_timeout_ms=30000,
)

def format_message(entry):
    return {
        "date": entry["date"],
        "front_left_c": entry["front_left_c"],
        "front_right_c": entry["front_right_c"],
        "back_left_c": entry["back_left_c"],
        "back_right_c": entry["back_right_c"],
    }

if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*.csv")), key=os.path.getmtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"Aucun CSV dans {DATA_DIR}")

    latest = files[0]
    data = read_csv_file(latest)

    print(f"[Producer] fichier={os.path.basename(latest)} lignes={len(data)}")

    for entry in data:
        producer.send(TOPIC, format_message(entry))

    producer.flush()
    print("[Producer] Done.")
