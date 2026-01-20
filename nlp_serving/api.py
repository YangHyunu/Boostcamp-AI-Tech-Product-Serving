from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, \
    AutoModelForSequenceClassification

router = APIRouter()
model = Auto
model = AutoModelForSequenceClassification.from_pretrained("klue/roberta-small")
tokenizer = AutoTokenizer.from_pretrained('klue/roberta-small', max_length=160)
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)


class PredictionRequest(BaseModel):
    text: str


class PredictionResponse(BaseModel):
    # label: str
    # score: float
    text: str


@router.post("/classify/")
async def classify_text(classify_in: PredictionRequest) -> PredictionResponse:
    # TODO: 텍스트를 받아서 모델로 추론하고 결과를 반환
    response = classify_in
    print(response)
    # response = pipeline(*classify_in)
    # print(response)
    return PredictionResponse(response.text)

