import os
import csv
import joblib
import pandas as pd
from sklearn.datasets import load_iris

from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.python import PythonOperator, BranchPythonOperator
from airflow.providers.slack.operators.slack import SlackAPIFileOperator
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 2, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


# TODO 1. get_samples 함수를 완성합니다
def get_samples() -> pd.DataFrame:
    iris = load_iris()

    data = iris.data
    target = iris.target
    feature_names = iris.feature_names

    
    dataset = pd.DataFrame(data, columns=feature_names)
    dataset['target'] = target
    random_samples = dataset.sample(n=5, random_state=42).reset_index(drop=True)
    # TODO: 한번 학습 시 랜덤한 5개 데이터 세트에 대한 학습을 수행하도록 구현합니다.
    #  실제 회사에서는 클라우드의 데이터 저장소나 데이터베이스에 있는 데이터를 가지고 와서 처리하지만,
    #  본 과제에서는 로컬에 있는 파일에서 랜덤으로 실험 세트를 추출해 예측하는 방식으로 진행합니다.
    return random_samples


# TODO 2. inference 함수를 완성합니다
def inference(**kwargs):
    model_path = os.path.join(os.curdir, "output", "model.joblib")

    # TODO:
    #  get_samples 함수를 통해 다운받은 dataset 를 가져옵니다.
    #  주어진 model_path 에서 학습된 모델을 불러옵니다.

    # Save file as csv format
    output_dir = os.path.join(os.curdir, "data")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%y%m%d%H%M")
    output_file = os.path.join(output_dir, f"predictions_{timestamp}.csv")
    import joblib
    model = joblib.load(model_path)
    samples = get_samples()
    X,y = samples.drop("target", axis=1), samples["target"]
    predictions = model.predict(X)
    predictions = pd.DataFrame(predictions, columns=["predicted_target"])
    predictions.to_csv(output_file, index=False)
    print(f"Predictions saved to {output_file}")
    # 반환값은 XCom으로 push 되어 다른 task에서 사용 가능합니다
    return output_file


# TODO 1. 5분에 1번씩 예측을 수행하는 DAG를 완성합니다. 주어진 두 함수를 활용합니다.
with DAG(
        dag_id='03-batch-inference',
        default_args=default_args,
        schedule="*/5 * * * *",  # Run every 5 minutes
        catchup=False,
        tags=['assignment'],
) as dag:
    execution_date = "{{ ds_nodash }}"
    get_sample_task =PythonOperator(task_id='get_sample_task',
                                    python_callable=get_samples)
    
    predict_task = PythonOperator(task_id="predict_task",
                                  python_callable=inference,
                                  op_kwargs={'execution_date': execution_date},
                                  do_xcom_push=True)
    
    send_task =SlackAPIFileOperator(
        task_id="slack_file_upload_2",
    slack_conn_id="slack_api_default",
    channels="#random",
    initial_comment="Hello World!",
    # 파일 경로를 predict_task가 반환한 XCom에서 가져옵니다
    filename="{{ ti.xcom_pull(task_ids='predict_task') }}",
    filetype="csv",
    )
    get_sample_task >> predict_task >> send_task