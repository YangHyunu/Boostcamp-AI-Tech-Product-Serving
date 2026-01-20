import os
import joblib
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from airflow.sdk import DAG ,task
from datetime import datetime, timedelta
from airflow.providers.standard.operators.python import PythonOperator  
from utils.slack_notifier import task_fail_slack_alert, task_succ_slack_alert

# Optional advanced task
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator

OUTPUT_DIR = os.path.join(os.curdir, "output")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2026, 1, 19),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),

}


def get_dataset() -> pd.DataFrame:
    iris = load_iris()

    data = iris.data
    target = iris.target
    feature_names = iris.feature_names

    dataset = pd.DataFrame(data, columns=feature_names)
    dataset['target'] = target

    return dataset


# TODO 1. train_model 함수를 완성합니다. train_model 을 통해 학습한 모델을 로컬 경로에 저장하게 됩니다.
def train_model(execution_date, **kwargs) -> str:
    # TODO: get_dataset 함수를 통해 다운받은 dataset 를 가져온 뒤, 모델을 학습합니다.
    # raise RuntimeError("Forced failure for webhook test")
    dataset = get_dataset()
    X = dataset.drop('target', axis=1).values
    y = dataset['target'].values

    # Train
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)

    score = model.score(X_test, y_test)
    print(f"model score: {score}")

    # TODO: 주어진 경로에 모델의 각 실행 버전을 나누어 저장합니다.
    # TODO: 저장된 모델의 경로를 반환합니다.
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model_path = os.path.join(OUTPUT_DIR,f"rf_model_{execution_date}.joblib")
    joblib.dump(model,model_path)
    return model_path


# TODO 2. 모델을 학습하는 DAG를 완성합니다. 주어진 함수 두 개를 활용합니다.
with (
    DAG(
        dag_id='01-simple-train',
        default_args=default_args,
        schedule="30 0 * * * ",
        catchup=False,
        tags=['assignment'],
        on_failure_callback = task_fail_slack_alert
) as dag):
    execution_date = "{{ ds_nodash }}"

    # TODO: 두 함수를 오퍼레이터를 통해 모델 학습을 수행합니다.
    get_data_task = PythonOperator(task_id='get_data_task',
                                   python_callable=get_dataset)
    train_model_task = PythonOperator(
        task_id='train_model_task',
        python_callable=train_model,
        op_kwargs={'execution_date': execution_date},

    )
    # LocalFilesystemToGCSOperator 를 이용하여 로컬이 아닌 GCS 버킷의 특정 경로에 파일을 업로드 해 봅니다.
    upload_to_gcs_task = LocalFilesystemToGCSOperator(
        task_id=f'upload_to_gcs',
        src="{{ ti.xcom_pull(task_ids='train_model_task') }}",
        dst="model.joblib",
        bucket='practice-bucket98',
        gcp_conn_id='gcp_connector',
    )
    # TODO: 심화/선택과제
    get_data_task >> train_model_task>> upload_to_gcs_task
    # >> upload_to_gcs_task
