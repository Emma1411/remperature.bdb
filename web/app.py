from flask import Flask, render_template, jsonify
import happybase
import pandas as pd
import numpy as np

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


def fetch_raw(limit=500):
    try:
        conn = happybase.Connection(host="hbase", port=9090, timeout=5000)
        conn.open()

        if b"temperature_raw" not in conn.tables():
            conn.close()
            return [], "Table temperature_raw introuvable."

        table = conn.table("temperature_raw")
        rows = []

        for key, data in table.scan(limit=limit):
            try:
                row = {
                    "rowkey": key.decode("utf-8"),
                    "date": data.get(b"d:date", b"").decode("utf-8"),
                    "front_left_c": float(data.get(b"d:front_left_c", b"0").decode("utf-8")),
                    "front_right_c": float(data.get(b"d:front_right_c", b"0").decode("utf-8")),
                    "back_left_c": float(data.get(b"d:back_left_c", b"0").decode("utf-8")),
                    "back_right_c": float(data.get(b"d:back_right_c", b"0").decode("utf-8")),
                }
                rows.append(row)
            except (KeyError, ValueError):
                continue

        conn.close()
        return rows, None

    except Exception as e:
        return [], f"Erreur lecture raw: {str(e)}"


@app.route("/")
def index():
    df_daily, warning_daily = fetch_daily()
    raw_rows, warning_raw = fetch_raw(limit=500)

    global_stats = sensor_stats = comparisons = anomalies = raw_datasets = box_data = {}
    raw_labels = []
    df_raw = pd.DataFrame()  # valeur par défaut

    if raw_rows:
        df_raw = pd.DataFrame(raw_rows)
        df_raw['date'] = pd.to_datetime(df_raw['date'], format='%m/%d/%Y %H:%M', errors='coerce')
        df_raw = df_raw.dropna(subset=['date'])  # important si format invalide
        df_raw = df_raw.sort_values('date')
        df_raw['avg_temp'] = df_raw[['front_left_c', 'front_right_c', 'back_left_c', 'back_right_c']].mean(axis=1)

        # Stats globales
        global_stats = {
            'total_measures': len(df_raw),
            'global_avg': round(df_raw['avg_temp'].mean(), 2) if not df_raw.empty else 0,
            'global_min': round(df_raw['avg_temp'].min(), 2) if not df_raw.empty else 0,
            'global_max': round(df_raw['avg_temp'].max(), 2) if not df_raw.empty else 0,
            'global_std': round(df_raw['avg_temp'].std(), 2) if not df_raw.empty else 0
        }

        # Stats par capteur
        sensor_stats = {}
        for sensor in ['front_left_c', 'front_right_c', 'back_left_c', 'back_right_c']:
            sensor_stats[sensor] = {
                'avg': round(df_raw[sensor].mean(), 2) if not df_raw.empty else 0,
                'min': round(df_raw[sensor].min(), 2) if not df_raw.empty else 0,
                'max': round(df_raw[sensor].max(), 2) if not df_raw.empty else 0,
                'std': round(df_raw[sensor].std(), 2) if not df_raw.empty else 0
            }

        # Comparaisons
        front_mean = df_raw[['front_left_c', 'front_right_c']].mean(axis=1).mean()
        back_mean  = df_raw[['back_left_c', 'back_right_c']].mean(axis=1).mean()
        left_mean  = df_raw[['front_left_c', 'back_left_c']].mean(axis=1).mean()
        right_mean = df_raw[['front_right_c', 'back_right_c']].mean(axis=1).mean()

        comparisons = {
            'front_vs_back': round(front_mean - back_mean, 2),
            'left_vs_right': round(left_mean - right_mean, 2)
        }

        # Anomalies (seulement hautes pour l'exemple)
        if not df_raw.empty and global_stats['global_std'] > 0:
            threshold = global_stats['global_avg'] + 2 * global_stats['global_std']
            anomalies = df_raw[df_raw['avg_temp'] > threshold].to_dict('records')
        else:
            anomalies = []

        # Charts data
        raw_labels = df_raw['date'].dt.strftime('%H:%M').tolist()
        raw_datasets = {
            'front_left': df_raw['front_left_c'].tolist(),
            'front_right': df_raw['front_right_c'].tolist(),
            'back_left': df_raw['back_left_c'].tolist(),
            'back_right': df_raw['back_right_c'].tolist()
        }

        box_data = [df_raw[s].tolist() for s in sensor_stats.keys()]

    # Daily data
    daily_labels = df_daily["date"].tolist() if not df_daily.empty else []
    daily_avg    = df_daily["avg_temperature"].tolist() if not df_daily.empty else []

    warning = warning_daily or warning_raw or ""

    return render_template(
        "index.html",
        table_daily     = df_daily.to_dict("records"),
        table_raw       = df_raw.to_dict("records")[:100],
        global_stats    = global_stats,
        sensor_stats    = sensor_stats,
        comparisons     = comparisons,
        anomalies       = anomalies,
        raw_labels      = raw_labels,
        raw_datasets    = raw_datasets,
        box_data        = box_data,
        daily_labels    = daily_labels,
        daily_avg       = daily_avg,
        warning         = warning
    )


# Route export (corrigée – on recalcule les données)
@app.route("/export/json")
def export_json():
    df_daily, _ = fetch_daily()
    raw_rows, _ = fetch_raw(limit=1000)  # limite raisonnable pour export

    daily_data = df_daily.to_dict("records") if not df_daily.empty else []

    raw_sample = []
    if raw_rows:
        df_raw_temp = pd.DataFrame(raw_rows)
        raw_sample = df_raw_temp.to_dict("records")

    payload = {
        "daily": {
            "warning": None,
            "data": daily_data
        },
        "raw": {
            "warning": "",
            "sample": raw_sample
        }
    }
    return jsonify(payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)