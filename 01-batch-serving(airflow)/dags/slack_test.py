from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator 
from datetime import datetime
from utils import slack

def get_min_value(**kwargs):
    x = 0
    y = 1
    z = 2
    x = z
    
    # 파이썬 내장 함수 min()을 사용하여 x와 y 중 작은 값을 반환합니다.
    return min(x, y) 

with DAG(
    dag_id="send_slack_message",
    start_date=datetime(2024, 10, 28),
    catchup=False,
    default_args={
        "on_failure_callback": slack.on_failure_callback,
    },
    tags=["operator_example"],
) as dag:
    task = PythonOperator(
        task_id="min_operator",
        python_callable=get_min_value, # 변경된 함수명 적용
    )