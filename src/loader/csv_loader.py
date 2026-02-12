import csv
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "temp", "data")

def read_csv_file(filepath):
    data = []
    with open(filepath, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            entry = {
                "date": row["date"],
                "front_left_c": float(row["front_left_c"]),
                "front_right_c": float(row["front_right_c"]),
                "back_left_c": float(row["back_left_c"]),
                "back_right_c": float(row["back_right_c"]),
            }
            data.append(entry)
    return data

def watch_for_new_files(poll_interval=2):
    processed_files = set()
    while True:
        for filename in os.listdir(DATA_DIR):
            if filename.endswith(".csv") and filename not in processed_files:
                filepath = os.path.join(DATA_DIR, filename)
                print(f"[Loader] Nouveau fichier détecté : {filename}")

                data = read_csv_file(filepath)
                processed_files.add(filename)

                yield data

        time.sleep(poll_interval)
