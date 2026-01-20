import os
import shutil
import joblib
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from airflow import DAG
from airflow.decorators import task
from datetime import datetime
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.python import PythonOperator
from utils.slack_notifier import task_succ_slack_alert , task_fail_slack_alert

OUTPUT_DIR = os.path.join(os.curdir, "output")

default_args = {
    "owner": "airflow",
    "start_date": datetime(2026, 1, 14),
    "end_date": datetime(2026, 1, 17),
}

def get_dataset() -> pd.DataFrame:
    iris = load_iris()
    dataset = pd.DataFrame(iris.data, columns=iris.feature_names)
    dataset["target"] = iris.target
    return dataset

# TODO 1. train_model 수정: random_state 추가로 점수 재현성 보장
@task(multiple_outputs=True, task_id="train_model_task")
def train_model(start_date, **kwargs) -> dict:
    dataset = get_dataset()
    X = dataset.drop("target", axis=1).values
    y = dataset["target"].values

    # random_state를 고정해야 테스트와 디버깅 시 점수가 변하지 않습니다.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    model = RandomForestClassifier(n_estimators=30, random_state=42)
    model.fit(X_train, y_train)

    score = model.score(X_test, y_test)
    
    os.makedirs(os.path.join(OUTPUT_DIR, "versions"), exist_ok=True)
    model_filename = f"model_{start_date}.joblib"
    model_path = os.path.join(OUTPUT_DIR, "versions", model_filename)
    joblib.dump(model, model_path)

    return {
        "score": score,
        "model_filename": model_filename,
        "start_date": start_date
    }

@task.branch(task_id="compare_model_performance")
def compare_model_performance(current_results, **kwargs):
    ti = kwargs['ti']
    # 과거 모든 실행의 score를 가져옴
    prev_data = ti.xcom_pull(
        task_ids="train_model_task",
        key="score",
        include_prior_dates=True
    )
    
    current_score = float(current_results['score'])

    if not prev_data:
        return "update_model_task"

    if not isinstance(prev_data, list):
        prev_data = [prev_data]

    # 현재 실행(리스트의 마지막 값)을 제외한 과거 최고점수 계산
    past_scores = [float(s) for s in prev_data[:-1] if s is not None]
    
    if not past_scores:
        return "update_model_task"

    max_prev_score = max(past_scores)
    print(f"Current: {current_score}, Max Past: {max_prev_score}")


    if current_score > max_prev_score:
        return "update_model_task"
    else:
        return "skip_task"

# TODO 3. 모델 저장 성공 시 Slack 알림 (on_success_callback)
@task(task_id="update_model_task", on_success_callback=task_succ_slack_alert)
def update_model(current_results):
    model_filename = current_results['model_filename']
    src_path = os.path.join(OUTPUT_DIR, "versions", model_filename)
    dst_path = os.path.join(OUTPUT_DIR, "model.joblib")
    
    shutil.copy(src_path, dst_path)
    print(f"Model updated: {model_filename}")

@task(task_id="skip_task", on_failure_callback=task_fail_slack_alert)
def skip_task():
    print("No improvement. Skip.")

with DAG(
    dag_id="02-model-selection",
    default_args=default_args,
    schedule="30 0 * * * ", # 한국시간 +9 니까 9:30 에 자동실행됨 매일
    catchup=True,
    tags=["assignment"],
) as dag:
    execution_date = "{{ ds_nodash }}"

    get_data_task = PythonOperator(
        task_id="get_data_task",
        python_callable=get_dataset,
    )

    # TODO 2. 태스크 연결 완성
    train_results = train_model(start_date=execution_date)
    branch_op = compare_model_performance(current_results=train_results)
    
    update_op = update_model(current_results=train_results)
    skip_op = skip_task()
    
    end = EmptyOperator(task_id="end", trigger_rule="one_success")
    
    get_data_task >> train_results >> branch_op
    branch_op >> [update_op, skip_op] >> end