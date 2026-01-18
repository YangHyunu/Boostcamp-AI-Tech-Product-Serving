from datetime import timedelta
from airflow.sdk import DAG,task
import textwrap
from datetime import datetime, timezone, timedelta
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator  
def print_hello():
        print("Hello, World!")
with DAG(
    dag_id ="hello_world_dag",
    description="Simple Hello World DAG",
    start_date=datetime(2026, 1, 10, tzinfo=timezone.utc),
    schedule="0 6 * * *",
    tags=["example", "hello_world"],
    catchup=False,
) as dag:

    hello_task = PythonOperator(
        task_id="print_hello_task",
        python_callable=print_hello,
    )

    bash_task = BashOperator(
        task_id="bash_hello_task",
        bash_command='echo "Hello from Bash!"',
    )

    templated_command = textwrap.dedent("""
        {% for i in range(5) %}
        echo "{{ data_interval_start.strftime('%Y-%m-%d') }}"
        echo "{{ (data_interval_start + macros.timedelta(days=7)).strftime('%Y-%m-%d') }}"
        {% endfor %}
""")

    t3 = BashOperator(
        task_id="templated",
        depends_on_past=False,
        bash_command=templated_command,
    )
    hello_task >> bash_task >> t3