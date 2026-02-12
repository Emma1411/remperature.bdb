from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="temperature_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,   # tu déclenches à la main
    catchup=False,
    tags=["temperature_topic", "temperature-group", "hbase"],
) as dag:

    init_hbase = BashOperator(
        task_id="init_hbase",
        bash_command="python /opt/airflow/src/hbase/hbase_init.py",
    )

    copy_csv = BashOperator(
        task_id="copy_csv_to_temp_data",
        bash_command="python /opt/airflow/src/loader/copy_latest_csv.py",
    )

    produce = BashOperator(
        task_id="produce_to_temperature_topic",
        bash_command="python /opt/airflow/src/kafka/producer_batch.py",
    )

    consume = BashOperator(
        task_id="consume_temperature_topic_to_hbase",
        bash_command="python /opt/airflow/src/kafka/consumer_batch_to_hbase.py",
    )

    aggregate = BashOperator(
        task_id="aggregate_to_temperature_daily",
        bash_command="python /opt/airflow/src/analysis/aggregate_daily.py",
    )

    init_hbase >> copy_csv >> produce >> consume >> aggregate
