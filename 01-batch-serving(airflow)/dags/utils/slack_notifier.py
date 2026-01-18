from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

SLACK_DAG_CONN_ID = "slack_dag_connection"

# 2. Webhook 함수 정의
def send_message(slack_msg):
    return SlackWebhookOperator(
        task_id="slack_webhook",
        slack_webhook_conn_id=SLACK_DAG_CONN_ID,
        message=slack_msg,
        username="Airflow-alert",
    )

def task_failure_alert(context):
    slack_msg = f"""
            :red_circle: Task Failed.
            *Task*: {context.get('task_instance').task_id}
            *Dag*: {context.get('task_instance').dag_id}
            *Execution Time*: {context.get('execution_date')}
            *Log Url*: {context.get('task_instance').log_url}
            """
    alert = send_message(slack_msg)
    return alert.execute(context=context)


def task_success_alert(context):
    slack_msg = f"""
            :large_green_circle: Task Succeeded.
            *Task*: {context.get('task_instance').task_id}
            *Dag*: {context.get('task_instance').dag_id}
            *Execution Time*: {context.get('execution_date')}
            *Log Url*: {context.get('task_instance').log_url}
            """
    alert = send_message(slack_msg)
    return alert.execute(context=context)
