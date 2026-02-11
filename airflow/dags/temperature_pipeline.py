from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator

args = {
    'owner': 'emmanuel',
    'start_date': days_ago(1)
}

dag = DAG(
    dag_id='pipeline',
    default_args=args,
    schedule_interval=None
)

with dag:

    task_1 = BashOperator(
        task_id='lancer_producer',
        bash_command='docker start producer || docker run -d --name producer --network remperaturebdb_default producer'
    )

    task_2 = BashOperator(
        task_id='lancer_consumer',
        bash_command='docker start consumer || docker run -d --name consumer --network remperaturebdb_default consumer'
    )

    task_3 = BashOperator(
        task_id='lancer_spark',
        bash_command='docker start spark || docker run -d --name spark --network remperaturebdb_default spark'
    )

    task_4 = BashOperator(
        task_id='fin_pipeline',
        bash_command='echo "Pipeline terminé avec succès."'
    )

    task_1 >> task_2 >> task_3 >> task_4