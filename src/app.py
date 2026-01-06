# app.py는 "FastAPI 서버"를 만드는 파일이에요!
# 마치 "웹 서버를 만드는 도구 상자" 같은 거예요!

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
import uvicorn
import os
import sys

# engine.py에서 HybridGraphRAGEngine을 가져와요!
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engine import HybridGraphRAGEngine
from config import print_config, validate_config

# --- [1] 전역 변수 ---
# engine은 "GraphRAG 엔진"이에요!
# None은 "아직 아무것도 없다"는 뜻이에요!
engine: HybridGraphRAGEngine = None

# --- [2] 서버 시작/종료 이벤트 핸들러 ---
# @asynccontextmanager는 "비동기 컨텍스트 매니저"를 만드는 거예요!
# 마치 "서버가 시작될 때와 끝날 때 뭔가를 하는" 것처럼!
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버가 시작될 때 실행되는 부분이에요!
    global engine
    
    # 설정 정보를 출력해요!
    print_config()
    
    # validate_config()는 "설정이 올바른지 확인하는" 함수예요!
    validate_config()
    
    # HybridGraphRAGEngine을 초기화하는 거예요!
    # 마치 "GraphRAG 엔진을 준비하는" 것처럼!
    print("🚀 HybridGraphRAGEngine 초기화 중...")
    engine = HybridGraphRAGEngine()
    print("✅ HybridGraphRAGEngine 준비 완료!")
    
    # yield는 "여기서 잠시 멈춰서 서버를 실행하고, 나중에 다시 돌아와"라는 뜻이에요!
    yield
    
    # 서버가 종료될 때 실행되는 부분이에요! (현재는 비어있어요)
    pass

# --- [3] FastAPI 앱 초기화 ---
# FastAPI()는 "웹 서버 앱을 만들어줘"라는 뜻이에요!
# lifespan은 "서버 시작/종료 이벤트 핸들러"예요!
app = FastAPI(
    title="VIK AI: Hybrid GraphRAG API",
    description="금융 분석을 위한 하이브리드 GraphRAG API예요! 인덱싱은 OpenAI API, 질문은 API/LOCAL 선택 가능해요!",
    version="2.0.0",
    lifespan=lifespan  # lifespan 이벤트 핸들러를 연결해요!
)

# --- [4] Pydantic 모델 ---
# Pydantic 모델은 "데이터 구조를 정의하는 것"이에요!
# 마치 "이런 모양의 데이터를 받을게요!"라고 미리 알려주는 거예요!

# QueryRequest는 "질문 요청"을 나타내는 모델이에요!
class QueryRequest(BaseModel):
    # question은 "질문 내용"이에요!
    question: str
    # mode는 "어떤 모드를 사용할지" 정하는 거예요. "api" 또는 "local"!
    # 기본값은 "local"이에요!
    mode: str = "local"
    
    # Pydantic v2 스타일로 예시 설정
    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "What is NVIDIA revenue?",
                "mode": "local"
            }
        }
    }

# InsertRequest는 "텍스트 추가 요청"을 나타내는 모델이에요!
class InsertRequest(BaseModel):
    # text는 "추가할 텍스트"예요!
    text: str
    
    # Pydantic v2 스타일로 설정 (deprecation warning 해결)
    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "NVIDIA reported record revenue of $57.0 billion in Q3 2026."
            }
        }
    }

# --- [5] 루트 엔드포인트 ---
# @app.get("/")는 "루트 경로(/)에 GET 요청이 오면" 실행되는 함수예요!
# 마치 "홈페이지에 접속하면" 실행되는 거예요!
@app.get("/")
async def root():
    # return은 "이걸 돌려줘"라는 뜻이에요!
    return {
        "message": "VIK AI Hybrid GraphRAG API에 오신 것을 환영해요!",
        "description": "인덱싱은 OpenAI API(gpt-5-mini)를 사용하고, 질문은 API/LOCAL 모드를 선택할 수 있어요!",
        "endpoints": {
            "/insert": "텍스트 인덱싱하기 (POST) - OpenAI API 사용",
            "/query": "질문하기 (POST) - mode 파라미터로 'api' 또는 'local' 선택",
            "/health": "서버 상태 확인 (GET)",
            "/graph_stats": "그래프 현황 확인 (GET)",
            "/visualize": "그래프 시각화 HTML 생성 (GET)",
            "/docs": "API 문서 보기 (GET)"
        },
        "usage": {
            "insert": {
                "method": "POST",
                "url": "/insert",
                "body": {"text": "인덱싱할 텍스트"}
            },
            "query": {
                "method": "POST",
                "url": "/query",
                "body": {
                    "question": "질문 내용",
                    "mode": "api 또는 local (기본값: local)"
                }
            }
        }
    }

# --- [6] 서버 상태 확인 엔드포인트 ---
# @app.get("/health")는 "서버 상태를 확인하는" 엔드포인트예요!
@app.get("/health")
async def health():
    # 서버가 잘 작동하고 있다는 것을 알려주는 거예요!
    return {
        "status": "healthy",
        "message": "서버가 정상적으로 작동 중이에요!",
        "engine_ready": engine is not None
    }

# --- [7] 그래프 통계 엔드포인트 ---
# @app.get("/graph_stats")는 "그래프 통계를 보여주는" 엔드포인트예요!
@app.get("/graph_stats")
async def graph_stats():
    # if는 "만약"이라는 뜻이에요!
    if engine is None:
        return {"nodes": 0, "edges": 0, "message": "엔진이 아직 초기화되지 않았어요!"}
    
    # engine.get_graph_stats()는 그래프 통계를 가져오는 거예요!
    return engine.get_graph_stats()

# --- [7-2] 그래프 초기화 엔드포인트 ---
# @app.post("/reset")는 "그래프를 초기화하는" 엔드포인트예요!
@app.post("/reset",
          summary="그래프 초기화",
          description="기존 그래프 스토리지를 백업하고 삭제한 후 새로운 그래프로 시작해요!")
async def reset_graph():
    # if는 "만약"이라는 뜻이에요!
    if engine is None:
        raise HTTPException(status_code=503, detail="엔진이 아직 초기화되지 않았어요!")
    
    try:
        import shutil
        from datetime import datetime
        
        # 백업 폴더 이름 생성 (타임스탬프 포함)
        backup_dir = f"{engine.working_dir}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 기존 그래프 스토리지가 있으면 백업
        if os.path.exists(engine.working_dir):
            shutil.move(engine.working_dir, backup_dir)
            print(f"✅ 기존 그래프 백업 완료: {backup_dir}")
        
        # 엔진 재초기화
        global engine
        engine = HybridGraphRAGEngine()
        
        return {
            "message": "그래프가 성공적으로 초기화되었어요!",
            "status": "success",
            "backup_dir": backup_dir if os.path.exists(backup_dir) else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"그래프 초기화 중 에러가 발생했어요: {str(e)}")

# --- [7-1] 그래프 시각화 엔드포인트 ---
# @app.get("/visualize")는 "그래프를 시각화하는 HTML 파일을 생성하는" 엔드포인트예요!
@app.get("/visualize",
         summary="그래프 시각화",
         description="GraphRAG 그래프를 인터랙티브하게 시각화한 HTML 파일을 생성해요!")
async def visualize():
    # if는 "만약"이라는 뜻이에요!
    if engine is None:
        raise HTTPException(status_code=503, detail="엔진이 아직 초기화되지 않았어요!")
    
    try:
        # visualize.py에서 visualize_graph 함수를 가져와요!
        from visualize import visualize_graph
        
        # 그래프를 시각화해서 HTML 파일을 생성해요!
        output_path = visualize_graph(working_dir=engine.working_dir, output_file="graph_visualization.html")
        
        if output_path and os.path.exists(output_path):
            # FileResponse는 "파일을 반환하는" 거예요!
            # 마치 "이 HTML 파일을 브라우저로 보여줘"라는 뜻이에요!
            return FileResponse(
                output_path,
                media_type="text/html",
                filename="graph_visualization.html"
            )
        else:
            raise HTTPException(status_code=500, detail="그래프 시각화 파일을 생성할 수 없어요!")
            
    except ImportError:
        raise HTTPException(status_code=500, detail="pyvis 패키지가 설치되지 않았어요! 'pip install pyvis'로 설치해주세요!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"그래프 시각화 중 에러가 발생했어요: {str(e)}")

# --- [8] 텍스트 인덱싱 엔드포인트 ---
# @app.post("/insert")는 "텍스트를 인덱싱하는" 엔드포인트예요!
# 인덱싱은 항상 OpenAI API를 사용해요! (정확한 금융 수치 추출을 위해)
@app.post("/insert", 
          summary="텍스트 인덱싱",
          description="텍스트를 GraphRAG에 인덱싱해요. 항상 OpenAI API를 사용해요!",
          response_description="인덱싱 결과")
async def insert(request: InsertRequest):
    # if는 "만약"이라는 뜻이에요!
    if engine is None:
        # HTTPException은 "에러를 던지는" 거예요!
        # 503은 "서비스를 사용할 수 없음"이라는 뜻이에요!
        raise HTTPException(status_code=503, detail="엔진이 아직 초기화되지 않았어요!")
    
    # text 필드가 비어있으면 에러를 발생시켜요!
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=422, 
            detail="'text' 필드는 비어있을 수 없어요! 텍스트를 입력해주세요."
        )
    
    try:
        # try는 "시도해봐"라는 뜻이에요!
        # engine.ainsert()는 비동기로 텍스트를 그래프에 넣는 거예요!
        # 인덱싱은 항상 OpenAI API를 사용해요!
        await engine.ainsert(request.text)
        
        # return은 "이걸 돌려줘"라는 뜻이에요!
        return {
            "message": "텍스트가 성공적으로 인덱싱되었어요! (OpenAI API 사용)",
            "status": "success",
            "mode": "openai_api"
        }
    except Exception as e:
        # except는 "만약 에러가 생기면"이라는 뜻이에요!
        # Exception은 "모든 종류의 에러"예요!
        # e는 에러 내용이에요!
        # HTTPException으로 에러를 반환해요!
        raise HTTPException(status_code=500, detail=f"인덱싱 중 에러가 발생했어요: {str(e)}")

# --- [9] 질문-답변 엔드포인트 ---
# @app.post("/query")는 "질문을 받아서 답변을 주는" 엔드포인트예요!
# mode 파라미터로 "api" 또는 "local"을 선택할 수 있어요!
@app.post("/query",
          summary="질문-답변",
          description="GraphRAG에 질문하고 답변을 받아요. mode로 'api' 또는 'local'을 선택할 수 있어요!\n\n**요청 형식**:\n```json\n{\n  \"question\": \"질문 내용\",\n  \"mode\": \"local\"\n}\n```",
          response_description="질문과 답변",
          responses={
              200: {
                  "description": "질문 성공",
                  "content": {
                      "application/json": {
                          "example": {
                              "question": "What is NVIDIA revenue?",
                              "answer": "NVIDIA's revenue is $57.0 billion in Q3 2026.",
                              "mode": "local",
                              "status": "success"
                          }
                      }
                  }
              },
              422: {
                  "description": "요청 데이터 형식 오류",
                  "content": {
                      "application/json": {
                          "example": {
                              "detail": [
                                  {
                                      "type": "missing",
                                      "loc": ["body", "question"],
                                      "msg": "Field required",
                                      "input": {}
                                  }
                              ]
                          }
                      }
                  }
              }
          })
async def query(request: QueryRequest):
    # if는 "만약"이라는 뜻이에요!
    if engine is None:
        raise HTTPException(status_code=503, detail="엔진이 아직 초기화되지 않았어요!")
    
    # question 필드가 비어있으면 에러를 발생시켜요!
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=422,
            detail="'question' 필드는 비어있을 수 없어요! 질문을 입력해주세요."
        )
    
    # mode가 "api" 또는 "local"이 아니면 에러를 발생시켜요!
    if request.mode not in ["api", "local"]:
        raise HTTPException(
            status_code=400,
            detail="mode는 'api' 또는 'local'이어야 해요! (현재 값: '{}')".format(request.mode)
        )
    
    try:
        # try는 "시도해봐"라는 뜻이에요!
        # engine.aquery()는 비동기로 질문에 답을 찾는 거예요!
        # request.mode에 따라 API 또는 LOCAL 모드를 사용해요!
        response = await engine.aquery(request.question, mode=request.mode)
        
        # return은 "이걸 돌려줘"라는 뜻이에요!
        return {
            "question": request.question,
            "answer": response,
            "mode": request.mode,
            "status": "success"
        }
    except Exception as e:
        # except는 "만약 에러가 생기면"이라는 뜻이에요!
        raise HTTPException(status_code=500, detail=f"질문 처리 중 에러가 발생했어요: {str(e)}")

# --- [10] 서버 실행 ---
# if __name__ == "__main__": 이건 "이 파일을 직접 실행했을 때만"이라는 뜻이에요!
if __name__ == "__main__":
    # uvicorn.run()은 "서버를 실행하는" 거예요!
    # app은 "FastAPI 앱"이에요!
    # host="0.0.0.0"은 "모든 네트워크 인터페이스에서 접속 가능"하다는 뜻이에요!
    # port=8000은 "8000번 포트를 사용한다"는 뜻이에요!
    uvicorn.run(app, host="0.0.0.0", port=8000)

