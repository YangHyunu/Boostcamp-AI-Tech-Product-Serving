from datetime import timedelta
from airflow.sdk import DAG ,task
from datetime import datetime, timezone, timedelta
from airflow.providers.standard.operators.python import PythonOperator  
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'start_date': datetime(2026, 1, 1, tzinfo=timezone.utc),
    'end_date':datetime(2026, 1, 13, tzinfo=timezone.utc),
}

    

def print_current_date():
    date_kor =["월","화","수","목","금","토","일"]
    date_now = datetime.now().date()
    datetime_weeknum = datetime.now().weekday()
    print(f"오늘은 {date_now} {date_kor[datetime_weeknum]}요일 입니다.")
def print_current_date_with_contxt(*args, **kwargs):
    print(f"kargs: {kwargs}")
    execution_date = kwargs.get('ds')
    execution_data_no_dash = kwargs["ds_nodash"]

    print(f"Execution date is {execution_date}")
    print(f"Execution date without dashes is {execution_data_no_dash}")
with DAG(
    dag_id="python_toy_dag",
    default_args=default_args,
    description="practice DAG using PythonOperator",
    schedule="0 14 * * *",  # KST 23:00 == UTC 14:00
    tags=["example", "python_toy"],
    catchup=True,
) as dag:
    python_task = PythonOperator(
        task_id="print_current_date_task",
        python_callable=print_current_date,)
    python_date_task = python_task
    @task
    def python_sleep(retries=2): # 만약 python_sleep이 실패하면 2번 재시도
        print("Sleeping for 5 seconds...")
    sleep_task = python_sleep()

    @task
    def python_pwd(task_id="python_pwd_task"):
        import os
        print("Current working directory:", os.getcwd())
    pwd_task = python_pwd()
    
    python_with_ctx = PythonOperator(
        task_id="print_current_date_with_context",
        python_callable=print_current_date_with_contxt,
        op_kwargs={  # Airflow 템플릿으로 ds, ds_nodash 전달
            "ds": "{{ ds }}",
            "ds_nodash": "{{ ds_nodash }}",
        },
    )
    python_with_ctx >> sleep_task
    python_date_task >> sleep_task # python_date_task가 먼저 실행된 후 sleep_task 실행
    python_date_task >> pwd_task # python_date_task가 먼저 실행된 후 pwd_task 실행
    # 병렬 실행
