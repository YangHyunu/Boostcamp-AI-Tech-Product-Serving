from datetime import timedelta
from airflow.sdk import DAG ,task
from datetime import datetime, timezone, timedelta
with DAG(
    dag_id ="bash_toy_dag",
    description="practice DAG using BashOperator",
    start_date=datetime(2026, 1, 10, tzinfo=timezone.utc),
    schedule="0 6 * * *",
    tags=["example", "bash_toy"],
) as dag:
    @task
    def bash_print_date():
        import os
        os.system('date')
    bash_task = bash_print_date()
    @task
    def bash_sleep(retries=2): # 만약 bash_sleep이 실패하면 2번 재시도
        import os
        os.system('sleep 5')
    sleep_task = bash_sleep()

    @task
    def bash_pwd(task_id="bash_pwd_task"):
        import os
        os.system('pwd')
    pwd_task = bash_pwd()

    bash_task >> sleep_task # bash_task가 먼저 실행된 후 sleep_task 실행
    bash_task >> pwd_task # bash_task가 먼저 실행된 후 pwd_task 실행
    # 병렬 실행