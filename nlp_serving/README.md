# NLP Serving - 문장 유사도 Online Serving

---

## 1. 과제 개요

본 과제는 **FastAPI**를 활용하여 문장 유사도(STS, Semantic Text Similarity) 예측 모델의 Online Serving API를 구축하는 실습입니다. Web Single Pattern으로 텍스트를 입력받아 실시간으로 유사도 점수를 반환합니다.

---

## 2. 과제 출제 목적 및 배경

NLP 모델은 텍스트 기반 서비스에서 핵심적인 역할을 합니다. 문장 유사도 예측은 검색 엔진, 챗봇, 추천 시스템 등 다양한 분야에서 활용됩니다.

이 과제를 통해 HuggingFace Transformers 기반 모델을 FastAPI로 서빙하는 방법, 토크나이저 활용, PyTorch Lightning 모델 로딩 등 NLP 서비스 구축에 필요한 기술을 익힙니다.

---

## 3. 과제 수행으로 얻어갈 수 있는 역량

- **FastAPI 기반 NLP API 설계**: 텍스트 입력 처리 및 응답 설계
- **Transformers 모델 서빙**: HuggingFace 모델 로드 및 추론
- **토크나이저 활용**: 텍스트 전처리 및 토큰화
- **PyTorch Lightning 모델 관리**: 학습된 체크포인트 로드
- **데이터베이스 연동**: SQLModel을 활용한 예측 결과 저장
- **Docker 컨테이너화**: NLP 서비스 배포

---

## 4. 과제 핵심 내용

### 모델 정보

| 항목    | 내용                                     |
| ------- | ---------------------------------------- |
| 모델    | `klue/roberta-small`                     |
| 태스크  | 문장 유사도 예측 (STS)                   |
| 입력    | 두 문장 (sentence_1, sentence_2)         |
| 출력    | 유사도 점수 (0.0 ~ 5.0)                  |

### 구현할 API 엔드포인트

| Method | Endpoint     | 설명                         |
| ------ | ------------ | ---------------------------- |
| POST   | `/predict`   | 두 문장의 유사도 점수 예측   |

### API 사용 예시

**Request:**
```bash
curl -X POST "http://0.0.0.0:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"sentence_1": "오늘 날씨가 정말 좋네요", "sentence_2": "날씨가 화창합니다"}'
```

**Response:**
```json
{"id": 1, "score": 4.2}
```

### 프로젝트 구조

```
nlp_serving/
├── main.py              # FastAPI 앱 엔트리포인트
├── api.py               # API 엔드포인트 정의 (구현 필요)
├── config.py            # 환경 설정 (모델 경로, DB URL 등)
├── database.py          # 데이터베이스 연결 설정
├── dependencies.py      # 의존성 관리
├── model.py             # 모델 클래스 및 데이터로더 정의
├── Dockerfile           # Docker 이미지 빌드 설정
├── data/
│   ├── train.csv        # 학습 데이터
│   ├── dev.csv          # 검증 데이터
│   ├── test.csv         # 테스트 데이터
│   ├── model.pt         # 학습된 모델 가중치
│   └── sample_submission.csv
├── poetry.lock
└── pyproject.toml
```

### 데이터셋 정보

- **KLUE STS Dataset**: 한국어 문장 유사도 데이터셋
- **컬럼**: id, sentence_1, sentence_2, label (0.0~5.0)

---

## 5. Required Packages

### 설치 및 실행

```bash
# Python 버전 확인 (3.9 ~ 3.12 권장, pyenv 사용 권장)
python --version

# Poetry 설치 및 패키지 설치
poetry install

# 모델 다운로드 (model.py 실행 시 자동 다운로드)
PYTHONPATH=. poetry run python model.py

# 서버 실행
PYTHONPATH=. poetry run python main.py

# 접속: http://localhost:8000/docs (Swagger UI)
```

### Docker 실행

```bash
# 이미지 빌드
docker build -t nlp-serving .

# 컨테이너 실행
docker run -p 8000:8000 nlp-serving
```

---

## 6. Reference

### 공식 문서

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers/)
- [KLUE Benchmark](https://klue-benchmark.com/)
- [PyTorch Lightning](https://lightning.ai/docs/pytorch/stable/)

---

WARNING: 본 교육 콘텐츠의 지식재산권은 재단법인 네이버커넥트에 귀속됩니다.
본 콘텐츠를 어떠한 경로로든 외부로 유출 및 수정하는 행위를 엄격히 금합니다.
다만, 비영리적 교육 및 연구활동에 한정되어 사용할 수 있으나 재단의 허락을 받아야 합니다.
이를 위반하는 경우, 관련 법률에 따라 책임을 질 수 있습니다.
