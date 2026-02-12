import happybase
import pandas as pd

TOP_N_COLDEST_DAYS = 5  # change à 10 si tu veux

connection = happybase.Connection(host="hbase", port=9090, timeout=5000)
connection.open()

raw_table = connection.table("temperature_raw")
daily_table = connection.table("temperature_daily")

rows = []
for _, data in raw_table.scan():
    # ---- lecture safe (si une colonne manque, on skip la ligne) ----
    try:
        date_str = data[b"d:date"].decode("utf-8")
        fl = float(data[b"d:front_left_c"].decode("utf-8"))
        fr = float(data[b"d:front_right_c"].decode("utf-8"))
        bl = float(data[b"d:back_left_c"].decode("utf-8"))
        br = float(data[b"d:back_right_c"].decode("utf-8"))
    except KeyError:
        # ligne "sale" (ancienne écriture), on ignore
        continue

    avg_temperature = (fl + fr + bl + br) / 4.0
    rows.append({"date": date_str, "avg_temperature": avg_temperature})

df = pd.DataFrame(rows)
if df.empty:
    print("[Aggregate] No valid data in temperature_raw (colonnes manquantes ou table vide)")
    connection.close()
    raise SystemExit(0)

# ---- parse date (ta date est du genre 4/11/2010 11:30) ----
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])
df["day"] = df["date"].dt.date

# ---- aggregation par jour ----
result = df.groupby("day").agg(
    count=("avg_temperature", "count"),
    avg_temperature=("avg_temperature", "mean"),
    min_temperature=("avg_temperature", "min"),
    max_temperature=("avg_temperature", "max"),
).reset_index()

# ---- écrire dans HBase temperature_daily ----
for _, r in result.iterrows():
    day = str(r["day"])
    daily_table.put(day.encode("utf-8"), {
        b"m:count": str(int(r["count"])).encode("utf-8"),
        b"m:avg_temperature": str(float(r["avg_temperature"])).encode("utf-8"),
        b"m:min_temperature": str(float(r["min_temperature"])).encode("utf-8"),
        b"m:max_temperature": str(float(r["max_temperature"])).encode("utf-8"),
    })

# ---- afficher les jours les plus froids ----
coldest = result.sort_values("avg_temperature", ascending=True).head(TOP_N_COLDEST_DAYS)

print("\n========== TOP JOURS LES PLUS FROIDS ==========")
for _, r in coldest.iterrows():
    print(
        f"{r['day']}  | avg={r['avg_temperature']:.2f}°C  "
        f"| min={r['min_temperature']:.2f}°C  | max={r['max_temperature']:.2f}°C  | n={int(r['count'])}"
    )
print("=============================================\n")

connection.close()
print(f"[Aggregate] Done. days={len(result)}")
