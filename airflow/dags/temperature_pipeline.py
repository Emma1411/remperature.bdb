from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

args = {
    'owner': 'emmanuel',
    'start_date': days_ago(1)
}

dag = DAG(
    dag_id='pipeline_temperature_simple',
    default_args=args,
    schedule_interval=None
)


def lancer_producer():
    print("Producer Kafka démarré (simulation).")
    print("Lecture des CSV et envoi vers Kafka...")

def lancer_spark():
    print("Job Spark Streaming démarré (simulation).")
    print("Lecture Kafka → transformation → écriture HBase...")

def fin_pipeline():
    print("Pipeline terminé avec succès.")


with dag:

    task_1 = BashOperator(
        task_id='demarrage_collecte',
        bash_command='echo "Démarrage du producer Kafka"'
    )

    task_2 = PythonOperator(
        task_id='lancer_producer',
        python_callable=lancer_producer
    )

    task_3 = PythonOperator(
        task_id='lancer_spark',
        python_callable=lancer_spark
    )

    task_4 = PythonOperator(
        task_id='fin_pipeline',
        python_callable=fin_pipeline
    )

    # Séquence d'exécution
    task_1 >> task_2 >> task_3 >> task_4
