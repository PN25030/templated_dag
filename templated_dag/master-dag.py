from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
from templated_dag import run_templated_dag  # Import the function from templated_dag.py

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 9, 29),
    'retries': 1,
}

# Define the DAG
with DAG(
    'templated_dag_execution',
    default_args=default_args,
    description='A DAG to execute templated_dag.py',
    schedule_interval=None,  # Run manually or define a cron schedule
    catchup=False,
) as dag:

    # Start task - dummy task
    start_task = DummyOperator(
        task_id='start_task'
    )

    # Python task to execute templated_dag.py logic
    templated_dag_execution = PythonOperator(
        task_id='execute_templated_dag',
        python_callable=run_templated_dag  # This points to the function in your script
    )

    # Stop task - dummy task
    stop_task = DummyOperator(
        task_id='stop_task'
    )

    # Task dependencies
    start_task >> templated_dag_execution >> stop_task
