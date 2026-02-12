import happybase

connection = happybase.Connection(host="hbase", port=9090)
connection.open()

if b"temperature_raw" not in connection.tables():
    connection.create_table("temperature_raw", {"d": dict()})

if b"temperature_daily" not in connection.tables():
    connection.create_table("temperature_daily", {"m": dict()})

connection.close()
print("[HBase] temperature_raw & temperature_daily OK")
