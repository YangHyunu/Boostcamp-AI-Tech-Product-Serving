# from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook
# def task_failure_alert(context):
#     print(f"Task has failed, task_instance_key_str: {context['task_instance_key_str']}")
    
# def dag_success_alert(context):
#     print(f"DAG has succeeded, run_id: {context['run_id']}")

# with DAG(
#     dag_id="slack_ex",
#     schedule="at_once",
#     catchup=False,
#     on_success_callback=dag_success_alert,
#     on_failure_callback=task_failure_alert,
#     tags=["example", "slack"],
# )

from airflow.sdk import Variable
import requests
 
def on_failure_callback(context):
    text = str(context["task_instance"])
    text += "```" + str(context.get("exception")) + "```"
    send_message_to_a_slack_channel(text, ":scream:")

def send_message_to_a_slack_channel(message, emoji_alias):
    url = Variable.get("slack_url")
    headers = {
        "content-type": "application/json",
    }
    data = {"text": f"[{emoji_alias}] {message}"}
    r = requests.post(url, json=data, headers=headers)
    return r