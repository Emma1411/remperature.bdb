from flask import Flask, render_template
import happybase
import pandas as pd

app = Flask(__name__)

def fetch_daily():
    try:
        conn = happybase.Connection(host="hbase", port=9090, timeout=5000)
        conn.open()

        if b"temperature_daily" not in conn.tables():
            conn.close()
            return pd.DataFrame([]), "Table temperature_daily introuvable (lance le DAG Airflow)."

        table = conn.table("temperature_daily")
        rows = []
        for key, data in table.scan():
            rows.append({
                "date": key.decode("utf-8"),
                "count": int(data.get(b"m:count", b"0").decode("utf-8")),
                "avg_temperature": float(data.get(b"m:avg_temperature", b"0").decode("utf-8")),
                "min_temperature": float(data.get(b"m:min_temperature", b"0").decode("utf-8")),
                "max_temperature": float(data.get(b"m:max_temperature", b"0").decode("utf-8")),
            })

        conn.close()
        df = pd.DataFrame(rows)
        if df.empty:
            return df, "Aucune donnée dans temperature_daily (lance le DAG Airflow)."
        return df.sort_values("date"), None
    except Exception as e:
        return pd.DataFrame([]), f"HBase/Thrift pas prêt: {e}"

@app.route("/")
def index():
    df, warning = fetch_daily()
    labels = df["date"].tolist() if not df.empty else []
    avg = df["avg_temperature"].tolist() if not df.empty else []
    return render_template("index.html", table=df.to_dict("records"), labels=labels, avg=avg, warning=warning)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
