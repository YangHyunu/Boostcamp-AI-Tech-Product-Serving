import os
import requests
import pandas as pd
from dotenv import load_dotenv
from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
# ...existing code...
load_dotenv()
# 추가: KST 현재 시각
current_time_kst = datetime.now(ZoneInfo("Asia/Seoul"))

OUTPUT_DIR = os.path.join(os.curdir, "data")
DOC_PATH = os.path.join(OUTPUT_DIR, "forecasts.csv")

FCST_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
SERVICE_KEY = os.getenv('FCST_SEVICE_KEY')


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2026, 1,17),
    'retries': 1,
    'retry_delay': timedelta(minutes=30),
}

params ={'serviceKey' : '이곳에 발급 받은 인증키 입력해주면 됩니다.', 'pageNo' : '2', 'numOfRows' : '10', 'dataType' : '응답 자료 형식', 'base_date' : '발표일자', 'base_time' : '발표시간', 'nx' : '예보지점 X 좌표', 'ny' : '예보지점 Y 좌표' }

# TODO 1. get_forecast 함수를 완성합니다
def get_forecast(page_num, lat, lng) -> pd.DataFrame:
    # 기준 날짜/시간을 KST(서울) 기준으로 설정
    base_date = current_time_kst.strftime("%Y%m%d")
    # API는 보통 직전 발표 시각을 요구하므로 1시간 전 시각을 사용합니다.
    base_time = (current_time_kst - timedelta(hours=18)).strftime("%H%M")

    params = {
        'authKey': SERVICE_KEY,
        'pageNo': str(page_num),
        'numOfRows': '10',
        'dataType': 'XML',
        'base_date': base_date,
        'base_time': base_time,
        'nx': str(lat),
        'ny': str(lng),
    }

    resp = requests.get(FCST_URL, params=params, timeout=10)
    try:
        resp.raise_for_status()
    except Exception:
        # 실패 시 상세 응답을 로그에 남기고 예외를 다시 던집니다
        print("Request failed:", getattr(resp, 'status_code', 'N/A'), resp.text)
        raise

    data = resp.json()
    items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
    df = pd.DataFrame(items)
    if df.empty:
        print("No forecast items returned from API")
    else:
        print(df.head())

    return df



if __name__ == "__main__":
    # 로컬에서 빠르게 동작 확인용 테스트 실행
    print("Testing get_forecast() with sample coordinates (nx=62, ny=125)")
    try:
        df = get_forecast(1, 55, 127)
        print(f"Returned {len(df)} rows")
    except Exception as e:
        print("get_forecast failed:", e)