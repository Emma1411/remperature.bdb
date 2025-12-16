import csv
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

DATA_DIR = os.path.join(BASE_DIR, "temp", "data")

TEMP_COLUMNS = [
    "front_left_c",
    "front_right_c",
    "back_left_c",
    "back_right_c",
]


def load_temperatures():
    data = []

    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".csv"):
            filepath = os.path.join(DATA_DIR, filename)

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


if __name__ == "__main__":
    temps = load_temperatures()
    print(f"{len(temps)} températures chargées")
    print(temps[:10])
