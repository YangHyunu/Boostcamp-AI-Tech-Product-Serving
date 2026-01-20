from airflow.providers.slack.operators.slack import SlackAPIOperator, SlackAPIPostOperator
from airflow.providers.slack.notifications.slack import send_slack_notification


from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta
from utils.slack_notifier import task_fail_slack_alert,task_succ_slack_alert
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 17),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'on_success_callback': [
    #         send_slack_notification(
    #             text="The DAG {{ dag.dag_id }} succeeded",
    #             channel="#alarm"
    #         )
    #     ],
    'on_failure_callback':task_fail_slack_alert,
    'on_success_callback': task_succ_slack_alert
}

execution_date = "{{ ds_nodash }}"
def error_handler():
    raise RuntimeError("의도적인 에러: 알림 테스트용")
dag = DAG(
    'Slack_test',
    default_args=default_args,
    description='A simple tutorial DAG',
    schedule=timedelta(days=1)
)

task1 = BashOperator(
    task_id ="bash1",
    bash_command='echo Heelo,',
    dag=dag
)
task2 = PythonOperator(
    task_id = "task2",
    python_callable=error_handler,
    op_kwargs={'execution_date':execution_date}
)
task1>>task2