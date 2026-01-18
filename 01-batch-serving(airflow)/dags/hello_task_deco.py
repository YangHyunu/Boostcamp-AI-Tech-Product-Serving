from datetime import timedelta
from airflow.sdk import DAG ,task
from datetime import datetime, timezone, timedelta


with DAG(
    dag_id ="hello_task_deco_dag",
    description="Hello World DAG using Task Decorators",
    start_date=datetime(2026, 1, 10, tzinfo=timezone.utc),
    schedule="0 6 * * *",
    tags=["example", "hello_task_deco"],
) as dag:
    @task
    def print_hello():
        print("Hello, World!")

    hello_task = print_hello(
)
    @task
    def bash_hello():
        import os
        os.system('echo "Hello from Bash!"')
    bash_task = bash_hello()

    hello_task >> bash_task
