from airflow.models import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

args = {
    'owner': 'pipis',
    'start_date': days_ago(1)
}

dag = DAG(
    dag_id='tp_docker_airflow',
    default_args=args,
    schedule_interval=None
)

def tache_2_func():
    print("Travail terminée")

tache_1 = BashOperator(
    task_id='tache_1_demarrage',
    bash_command='echo "Démarrage de la collecte de données"',
    dag=dag
)

tache_2 = PythonOperator(
    task_id='tache_2_collecte',
    python_callable=tache_2_func,
    dag=dag
)

tache_3 = BashOperator(
    task_id='tache_3_fin',
    bash_command='echo "Fin du traitement"',
    dag=dag
)

tache_1 >> tache_2 >> tache_3
