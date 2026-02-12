import json
import happybase
from kafka import KafkaConsumer

TOPIC = "temperature_topic"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers="kafka:29092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="temperature-group",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    consumer_timeout_ms=10000
)

def main():
    conn = happybase.Connection("hbase", 9090, timeout=5000)
    conn.open()
    table = conn.table("temperature_raw")

    counter = 0

    for msg in consumer:
        data = msg.value

        rowkey = f"{data['date']}#{counter}".encode("utf-8")

        table.put(rowkey, {
            b"d:date": str(data["date"]).encode("utf-8"),
            b"d:front_left_c": str(data["front_left_c"]).encode("utf-8"),
            b"d:front_right_c": str(data["front_right_c"]).encode("utf-8"),
            b"d:back_left_c": str(data["back_left_c"]).encode("utf-8"),
            b"d:back_right_c": str(data["back_right_c"]).encode("utf-8"),
        })

        counter += 1

    conn.close()
    print(f"[Consumer] inserted={counter}")

if __name__ == "__main__":
    main()
