from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime

default_args = {
    "owner": "emmanuel",
    "start_date": datetime(2025, 1, 1),
}

with DAG(
    dag_id="temperature_streaming_pipeline",
    default_args=default_args,
    schedule_interval="@once",
    catchup=False,
) as dag:

    start_producer = DockerOperator(
        task_id="start_producer",
        image="remperature-producer:latest",
        command="python -m src.producer.kafka_producer",
        network_mode="remperature-bdb_default",
        auto_remove=True,
    )

    start_spark_streaming = DockerOperator(
        task_id="start_spark_streaming",
        image="remperature-spark-job:latest",
        command="spark-submit /app/streaming_job.py",
        network_mode="remperature-bdb_default",
        auto_remove=True,
    )

    start_producer >> start_spark_streaming
