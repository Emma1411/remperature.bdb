from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, FloatType
import happybase


schema = StructType([
    StructField("timestamp", StringType(), True),
    StructField("temperature", StructType([
        StructField("date", StringType(), True),
        StructField("front_left_c", FloatType(), True),
        StructField("front_right_c", FloatType(), True),
        StructField("back_left_c", FloatType(), True),
        StructField("back_right_c", FloatType(), True)
    ]), True)
])


spark = SparkSession.builder \
    .appName("KafkaToHBase") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "temperature_topic") \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .option("kafka.metadata.max.age.ms", "10000") \
    .load()


parsed_df = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select(
    col("data.timestamp"),
    col("data.temperature.date").alias("date"),
    col("data.temperature.front_left_c"),
    col("data.temperature.front_right_c"),
    col("data.temperature.back_left_c"),
    col("data.temperature.back_right_c")
)


def write_batch_to_hbase(batch_df, batch_id):
    if batch_df.count() == 0:
        return

    rows = batch_df.collect()

    connection = happybase.Connection(host='hbase', port=9090)
    table = connection.table('temperature_data')

    for row in rows:
        if row['date'] is None:
            continue
        rowkey = str(row['date']).encode('utf-8')
        table.put(rowkey, {
            b'cf:date': str(row['date']).encode('utf-8'),
            b'cf:front_left_c': str(row['front_left_c'] or 0.0).encode('utf-8'),
            b'cf:front_right_c': str(row['front_right_c'] or 0.0).encode('utf-8'),
            b'cf:back_left_c': str(row['back_left_c'] or 0.0).encode('utf-8'),
            b'cf:back_right_c': str(row['back_right_c'] or 0.0).encode('utf-8'),
        })

    connection.close()


query = parsed_df.writeStream \
    .foreachBatch(write_batch_to_hbase) \
    .outputMode("append") \
    .option("checkpointLocation", "/tmp/checkpoint_hbase") \
    .start()

query.awaitTermination()