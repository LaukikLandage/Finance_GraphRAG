# FastAPI는 웹 API를 쉽게 만들 수 있게 해주는 도구예요!
# 마치 "웹 서버를 만드는 도구 상자" 같은 거예요!
from fastapi import FastAPI, HTTPException
# uvicorn은 FastAPI 서버를 실행하는 도구예요!
# 마치 "서버를 켜는 스위치" 같은 거예요!
import uvicorn
# Pydantic은 데이터 검증을 해주는 도구예요!
# 마치 "데이터가 올바른지 확인하는 검사관" 같은 거예요!
from pydantic import BaseModel
# asyncio는 비동기 프로그래밍을 할 수 있게 해주는 도구예요!
import asyncio
# main.py에서 만든 함수들을 가져와요!
# sys.path.append()는 "이 경로도 찾아봐"라는 뜻이에요!
import sys
import os
# 현재 파일의 폴더 경로를 추가해요!
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# main.py에서 함수들을 가져와요!
from main import ollama_model_if, ollama_embedding_if
from nano_graphrag import GraphRAG

# FastAPI 앱을 만드는 거예요!
# FastAPI()는 "웹 서버 앱을 만들어줘"라는 뜻이에요!
app = FastAPI(
    title="Financial GraphRAG API",  # API의 이름이에요!
    description="금융 보고서를 분석하는 GraphRAG API예요!",  # API 설명이에요!
    version="1.0.0"  # 버전이에요!
)

# GraphRAG 인스턴스를 전역 변수로 만들어요!
# 전역 변수는 "어디서든 쓸 수 있는 변수"예요!
# None은 "아직 아무것도 없다"는 뜻이에요!
graph_rag = None

# Pydantic 모델은 "데이터 구조를 정의하는 것"이에요!
# 마치 "이런 모양의 데이터를 받을게요!"라고 미리 알려주는 거예요!

# QueryRequest는 "질문 요청"을 나타내는 모델이에요!
class QueryRequest(BaseModel):
    # question은 "질문 내용"이에요!
    # str은 "문자열(텍스트)"이라는 뜻이에요!
    question: str

# InsertRequest는 "텍스트 추가 요청"을 나타내는 모델이에요!
class InsertRequest(BaseModel):
    # text는 "추가할 텍스트"예요!
    text: str

# @app.on_event("startup")는 "서버가 시작될 때" 실행되는 함수예요!
# async def는 "비동기 함수"를 만드는 거예요!
@app.on_event("startup")
async def startup_event():
    # global은 "전역 변수를 사용하겠다"는 뜻이에요!
    global graph_rag
    # GraphRAG를 초기화하는 거예요!
    # 마치 "GraphRAG 도구를 준비하는" 것처럼!
    print("🚀 GraphRAG 초기화 중...")
    graph_rag = GraphRAG(
        working_dir="./my_graph_data",
        best_model_func=ollama_model_if,
        cheap_model_func=ollama_model_if,
        embedding_func=ollama_embedding_if
    )
    print("✅ GraphRAG 준비 완료!")

# @app.get("/")는 "루트 경로(/)에 GET 요청이 오면" 실행되는 함수예요!
# 마치 "홈페이지에 접속하면" 실행되는 거예요!
@app.get("/")
async def root():
    # return은 "이걸 돌려줘"라는 뜻이에요!
    return {
        "message": "Financial GraphRAG API에 오신 것을 환영해요!",
        "endpoints": {
            "/query": "질문하기 (POST)",
            "/insert": "텍스트 추가하기 (POST)",
            "/health": "서버 상태 확인 (GET)",
            "/docs": "API 문서 보기 (GET)"
        }
    }

# @app.get("/health")는 "서버 상태를 확인하는" 엔드포인트예요!
@app.get("/health")
async def health():
    # 서버가 잘 작동하고 있다는 것을 알려주는 거예요!
    return {"status": "healthy", "message": "서버가 정상적으로 작동 중이에요!"}

# @app.post("/query")는 "질문을 받아서 답변을 주는" 엔드포인트예요!
# POST는 "데이터를 보낼 때" 사용하는 HTTP 메서드예요!
@app.post("/query")
async def query(request: QueryRequest):
    # if는 "만약"이라는 뜻이에요!
    # graph_rag가 None이면 (아직 초기화되지 않았으면)
    if graph_rag is None:
        # HTTPException은 "에러를 던지는" 거예요!
        # 503은 "서비스를 사용할 수 없음"이라는 뜻이에요!
        raise HTTPException(status_code=503, detail="GraphRAG가 아직 초기화되지 않았어요!")
    
    try:
        # try는 "시도해봐"라는 뜻이에요!
        # graph_rag.aquery()는 비동기로 질문에 답을 찾는 거예요!
        # await는 "답변이 올 때까지 기다려"라는 뜻이에요!
        response = await graph_rag.aquery(request.question)
        # return은 "이걸 돌려줘"라는 뜻이에요!
        return {
            "question": request.question,
            "answer": response,
            "status": "success"
        }
    except Exception as e:
        # except는 "만약 에러가 생기면"이라는 뜻이에요!
        # Exception은 "모든 종류의 에러"예요!
        # e는 에러 내용이에요!
        # HTTPException으로 에러를 반환해요!
        raise HTTPException(status_code=500, detail=f"질문 처리 중 에러가 발생했어요: {str(e)}")

# @app.post("/insert")는 "텍스트를 추가하는" 엔드포인트예요!
@app.post("/insert")
async def insert(request: InsertRequest):
    # if는 "만약"이라는 뜻이에요!
    if graph_rag is None:
        raise HTTPException(status_code=503, detail="GraphRAG가 아직 초기화되지 않았어요!")
    
    try:
        # graph_rag.ainsert()는 비동기로 텍스트를 그래프에 넣는 거예요!
        await graph_rag.ainsert(request.text)
        return {
            "message": "텍스트가 성공적으로 추가되었어요!",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텍스트 추가 중 에러가 발생했어요: {str(e)}")

# if __name__ == "__main__": 이건 "이 파일을 직접 실행했을 때만"이라는 뜻이에요!
if __name__ == "__main__":
    # uvicorn.run()은 "서버를 실행하는" 거예요!
    # app은 "FastAPI 앱"이에요!
    # host="0.0.0.0"은 "모든 네트워크 인터페이스에서 접속 가능"하다는 뜻이에요!
    # port=8000은 "8000번 포트를 사용한다"는 뜻이에요!
    uvicorn.run(app, host="0.0.0.0", port=8000)

