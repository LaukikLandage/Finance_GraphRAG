# engine.py는 "GraphRAG 엔진"을 만드는 파일이에요!
# 마치 "자동차의 엔진"처럼, 이 파일이 실제로 GraphRAG를 작동시켜요!

import os
import asyncio
import sys
from typing import Optional, Literal
from nano_graphrag import GraphRAG
from openai import AsyncOpenAI
from ollama import AsyncClient

# graspologic 패키지가 없을 때를 대비한 더미 모듈
# graspologic는 그래프 클러스터링에 사용되는데, 설치가 어려워서 더미로 대체해요!
try:
    import graspologic
    import graspologic.utils
except ImportError:
    # graspologic가 없으면 더미 모듈을 만들어요!
    class DummyGraspologic:
        class partition:
            @staticmethod
            def hierarchical_leiden(*args, **kwargs):
                # 더미 함수 - 빈 결과 반환
                return {}
        
        class utils:
            # utils 모듈의 함수들도 더미로 만들어요!
            @staticmethod
            def largest_connected_component(graph):
                # 더미 함수 - 그래프 그대로 반환
                return graph
    
    # sys.modules에 더미 모듈을 등록해요!
    sys.modules['graspologic'] = DummyGraspologic()
    sys.modules['graspologic.partition'] = DummyGraspologic.partition
    sys.modules['graspologic.utils'] = DummyGraspologic.utils
    print("⚠️  graspologic가 없어서 더미 모듈을 사용해요. 클러스터링 기능이 제한될 수 있어요.")

# config.py에서 설정을 가져와요!
from config import (
    RUN_MODE,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    API_MODELS,
    LOCAL_MODELS,
    WORKING_DIR,
    get_models,
    validate_config,
)

# --- [1] OpenAI API를 사용하는 LLM 함수 (인덱싱용 - 금융 특화) ---
# openai_model_if는 OpenAI API를 사용해서 AI에게 질문하는 함수예요!
# async def는 "비동기 함수"를 만드는 거예요. 마치 "나중에 실행될 함수"를 만드는 것처럼!
# prompt는 "질문 내용"이에요. AI에게 물어볼 내용이에요!
# system_prompt는 "시스템 메시지"예요. AI에게 "너는 이런 역할이야"라고 알려주는 거예요!
# history_messages는 "이전 대화 내용"이에요!
# **kwargs는 "나머지 모든 인자"를 받는 거예요. 마치 "뭐든지 다 받아줄게"라는 뜻이에요!
async def openai_model_if(prompt: str, system_prompt: Optional[str] = None, history_messages: list = [], **kwargs) -> str:
    # AsyncOpenAI()는 OpenAI API와 비동기로 대화할 수 있는 클라이언트예요!
    # 마치 전화기를 만드는 것처럼!
    client = AsyncOpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    
    # messages는 "대화 내용을 담을 상자"예요!
    messages = []
    
    # if는 "만약"이라는 뜻이에요!
    # system_prompt가 있으면 시스템 메시지를 추가해요!
    # 인덱싱할 때는 금융 특화 프롬프트를 기본으로 사용해요!
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    elif "entity_extraction" in str(kwargs) or "extract" in prompt.lower():
        # 엔티티 추출 작업일 때는 금융 특화 프롬프트를 자동으로 추가해요!
        financial_prompt = get_financial_entity_prompt()
        messages.append({"role": "system", "content": financial_prompt})
    
    # history_messages는 "이전 대화 내용"이에요!
    messages.extend(history_messages)
    
    # 사용자의 질문을 추가해요!
    messages.append({"role": "user", "content": prompt})
    
    # API_MODELS["llm"]은 "gpt-5-mini"예요!
    # client.chat.completions.create()는 OpenAI API에 요청을 보내는 거예요!
    # 마치 "AI에게 질문하는" 것처럼!
    response = await client.chat.completions.create(
        model=API_MODELS["llm"],
        messages=messages,
        temperature=0.1,  # temperature는 "창의성"을 조절하는 거예요. 0.1은 정확하게 답하라는 뜻이에요!
    )
    
    # response.choices[0].message.content는 AI가 답한 내용을 가져오는 거예요!
    # 마치 AI가 답변한 내용을 꺼내는 것처럼!
    return response.choices[0].message.content

# --- [2] Ollama를 사용하는 LLM 함수 ---
# ollama_model_if는 Ollama를 사용해서 AI에게 질문하는 함수예요!
async def ollama_model_if(prompt: str, system_prompt: Optional[str] = None, history_messages: list = [], **kwargs) -> str:
    # AsyncClient()는 Ollama 서버와 비동기로 대화할 수 있는 클라이언트예요!
    client = AsyncClient()
    
    # messages는 "대화 내용을 담을 상자"예요!
    messages = []
    
    # system_prompt가 있으면 시스템 메시지를 추가해요!
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # history_messages는 "이전 대화 내용"이에요!
    messages.extend(history_messages)
    
    # 사용자의 질문을 추가해요!
    messages.append({"role": "user", "content": prompt})
    
    # LOCAL_MODELS["llm"]은 "llama3.2:3b"예요!
    # client.chat()는 Ollama 서버에 요청을 보내는 거예요!
    response = await client.chat(model=LOCAL_MODELS["llm"], messages=messages)
    
    # response['message']['content']는 AI가 답한 내용을 가져오는 거예요!
    return response['message']['content']

# --- [3] OpenAI API를 사용하는 Embedding 함수 ---
# openai_embedding_if는 OpenAI API를 사용해서 텍스트를 숫자 벡터로 바꾸는 함수예요!
# texts는 "텍스트들의 리스트"예요. 여러 텍스트를 한 번에 변환할 수 있어요!
async def openai_embedding_if(texts: list[str]) -> list[list[float]]:
    # AsyncOpenAI()는 OpenAI API와 비동기로 대화할 수 있는 클라이언트예요!
    client = AsyncOpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
    
    # embeds는 "변환된 숫자 벡터들을 담을 상자"예요!
    embeds = []
    
    # for는 반복문이에요. texts 안에 있는 각 text를 하나씩 꺼내서 반복하는 거예요!
    for text in texts:
        # client.embeddings.create()는 텍스트를 숫자 벡터로 변환하는 거예요!
        # model=API_MODELS["embedding"]은 "text-embedding-3-small"을 사용한다는 뜻이에요!
        response = await client.embeddings.create(
            model=API_MODELS["embedding"],
            input=text,
        )
        
        # response.data[0].embedding은 변환된 숫자 벡터예요!
        # embeds.append()는 embeds 상자에 숫자 벡터를 넣는 거예요!
        embeds.append(response.data[0].embedding)
    
    # return은 "이걸 돌려줘"라는 뜻이에요. 변환된 벡터들을 반환해요!
    return embeds

# embedding_dim은 "숫자 벡터의 크기"예요!
# text-embedding-3-small 모델은 1536차원 벡터를 만들어요!
openai_embedding_if.embedding_dim = API_MODELS["embedding_dim"]

# --- [4] Ollama를 사용하는 Embedding 함수 ---
# ollama_embedding_if는 Ollama를 사용해서 텍스트를 숫자 벡터로 바꾸는 함수예요!
async def ollama_embedding_if(texts: list[str]) -> list[list[float]]:
    # AsyncClient()는 Ollama 서버와 비동기로 대화할 수 있는 클라이언트예요!
    client = AsyncClient()
    
    # embeds는 "변환된 숫자 벡터들을 담을 상자"예요!
    embeds = []
    
    # for는 반복문이에요. texts 안에 있는 각 text를 하나씩 꺼내서 반복하는 거예요!
    for text in texts:
        # client.embeddings()는 텍스트를 숫자 벡터로 변환하는 거예요!
        # model=LOCAL_MODELS["embedding"]은 "nomic-embed-text"를 사용한다는 뜻이에요!
        response = await client.embeddings(model=LOCAL_MODELS["embedding"], prompt=text)
        
        # response['embedding']은 변환된 숫자 벡터예요!
        # embeds.append()는 embeds 상자에 숫자 벡터를 넣는 거예요!
        embeds.append(response['embedding'])
    
    # return은 "이걸 돌려줘"라는 뜻이에요. 변환된 벡터들을 반환해요!
    return embeds

# embedding_dim은 "숫자 벡터의 크기"예요!
# nomic-embed-text 모델은 768차원 벡터를 만들어요!
ollama_embedding_if.embedding_dim = LOCAL_MODELS["embedding_dim"]

# --- [5] 금융 특화 엔티티 추출 프롬프트 ---
# get_financial_entity_prompt()는 "금융 엔티티를 추출하기 위한 프롬프트"를 만드는 함수예요!
def get_financial_entity_prompt() -> str:
    # 이 프롬프트는 NanoGraphRAG가 엔티티를 추출할 때 사용해요!
    # 금융 지표를 우선적으로 추출하도록 설정해요!
    prompt = """You are a financial analyst extracting entities from financial documents.

Focus on extracting the following financial entities with HIGH PRIORITY:
- REVENUE (매출, Revenue, Sales, Total Revenue)
- OPERATING_INCOME (영업이익, Operating Income, Operating Profit)
- NET_INCOME (순이익, Net Income, Profit)
- GROWTH_RATE (성장률, Growth Rate, YoY Growth, QoQ Growth)
- MARGIN (마진, Gross Margin, Operating Margin, Net Margin)
- ASSET (자산, Total Assets, Current Assets)
- LIABILITY (부채, Total Liabilities, Current Liabilities)
- EQUITY (자본, Shareholders' Equity, Equity)
- CASH_FLOW (현금흐름, Operating Cash Flow, Free Cash Flow)
- EPS (주당순이익, Earnings Per Share, EPS)
- PE_RATIO (주가수익비율, P/E Ratio, Price-to-Earnings)
- MARKET_CAP (시가총액, Market Capitalization, Market Cap)

Also extract standard entities:
- ORGANIZATION (회사명, 기관명)
- PERSON (인물명, 임원명)
- GEO (지역, 국가, 도시)
- DATE (날짜, 분기, 연도)
- TECHNOLOGY (기술명, 제품명)

For each entity, extract:
1. The exact name/value
2. The entity type
3. The context (where it appears in the document)
4. Relationships to other entities (e.g., "NVIDIA's revenue is $57.0B")

Be precise with financial numbers. Extract exact values with units (e.g., "$57.0 billion", "23.5%", "Q3 2026").
"""
    return prompt

# --- [6] GraphRAG 엔진 클래스 ---
# HybridGraphRAGEngine은 "하이브리드 GraphRAG 엔진"이에요!
# 마치 "자동차 엔진"처럼, 이 클래스가 GraphRAG를 작동시켜요!
class HybridGraphRAGEngine:
    # __init__은 "초기화 함수"예요. 클래스를 만들 때 자동으로 실행되는 함수예요!
    # 마치 "자동차를 만들 때 엔진을 준비하는" 것처럼!
    def __init__(self, working_dir: Optional[str] = None):
        # validate_config()는 "설정이 올바른지 확인하는" 함수예요!
        validate_config()
        
        # working_dir이 없으면 기본값을 사용해요!
        self.working_dir = working_dir or WORKING_DIR
        
        # os.makedirs()는 폴더를 만드는 거예요. exist_ok=True는 "이미 있으면 괜찮아"라는 뜻이에요!
        os.makedirs(self.working_dir, exist_ok=True)
        
        # 인덱싱용 GraphRAG 인스턴스 (항상 OpenAI API 사용)
        # 인덱싱(공부)할 때는 정확한 금융 수치를 추출하기 위해 OpenAI API를 써요!
        # 기본 클러스터링 알고리즘 사용 (graspologic 더미 모듈로 처리)
        self.indexing_rag = GraphRAG(
            working_dir=self.working_dir,
            best_model_func=openai_model_if,      # OpenAI API 사용!
            cheap_model_func=openai_model_if,    # OpenAI API 사용!
            embedding_func=openai_embedding_if,  # OpenAI Embedding 사용!
        )
        
        # 질문용 GraphRAG 인스턴스들 (API/LOCAL 선택 가능)
        # 중요: 같은 그래프 데이터를 사용하므로 embedding도 같아야 해요!
        # 인덱싱할 때 OpenAI embedding(1536차원)을 사용했으니, 질문할 때도 같은 embedding을 사용해요!
        self.query_rag_api = GraphRAG(
            working_dir=self.working_dir,  # 같은 그래프 데이터를 사용해요!
            best_model_func=openai_model_if,
            cheap_model_func=openai_model_if,
            embedding_func=openai_embedding_if,  # 인덱싱과 같은 embedding 사용!
        )
        
        # LOCAL 모드도 같은 embedding을 사용해요! (그래프 데이터와 호환되도록)
        # LLM만 Ollama를 사용하고, embedding은 OpenAI를 사용해요!
        self.query_rag_local = GraphRAG(
            working_dir=self.working_dir,  # 같은 그래프 데이터를 사용해요!
            best_model_func=ollama_model_if,  # LLM만 Ollama 사용!
            cheap_model_func=ollama_model_if,
            embedding_func=openai_embedding_if,  # Embedding은 OpenAI 사용 (인덱싱과 동일)!
        )
        
        print(f"✅ HybridGraphRAGEngine 초기화 완료!")
        print(f"📁 작업 디렉토리: {self.working_dir}")
        print(f"📚 인덱싱 모드: OpenAI API (gpt-5-mini)")
        print(f"💬 질문 모드: API 또는 LOCAL 선택 가능")
    
    # ainsert()는 "비동기로 텍스트를 그래프에 넣는" 함수예요!
    # text는 "추가할 텍스트"예요!
    async def ainsert(self, text: str) -> None:
        # indexing_rag.ainsert()는 OpenAI API를 사용해서 인덱싱하는 거예요!
        # 마치 "정확하게 공부하는" 것처럼!
        await self.indexing_rag.ainsert(text)
        print("✅ 인덱싱 완료! (OpenAI API 사용)")
    
    # aquery()는 "비동기로 질문에 답을 찾는" 함수예요!
    # question은 "질문 내용"이에요!
    # mode는 "어떤 모드를 사용할지" 정하는 거예요. "api" 또는 "local"!
    async def aquery(self, question: str, mode: Literal["api", "local"] = "local") -> str:
        # 디버깅: 질문 내용 출력
        print(f"🔍 [DEBUG] 질문: {question}")
        print(f"🔍 [DEBUG] 모드: {mode}")
        print(f"🔍 [DEBUG] 작업 디렉토리: {self.working_dir}")
        
        # 그래프 파일이 있는지 확인해요!
        graphml_path = os.path.join(self.working_dir, "graph_chunk_entity_relation.graphml")
        if os.path.exists(graphml_path):
            import networkx as nx
            G = nx.read_graphml(graphml_path)
            print(f"🔍 [DEBUG] 그래프 노드 수: {G.number_of_nodes()}, 엣지 수: {G.number_of_edges()}")
        else:
            print(f"⚠️  [DEBUG] 그래프 파일이 없어요: {graphml_path}")
        
        # if는 "만약"이라는 뜻이에요!
        if mode == "api":
            # API 모드면 OpenAI API를 사용해서 답변을 생성해요!
            # 마치 "정확하게 답하는" 것처럼!
            print(f"💬 질문 모드: OpenAI API")
            print(f"🔍 [DEBUG] query_rag_api.aquery() 호출 시작...")
            try:
                # QueryParam을 명시적으로 설정해서 테스트해요!
                from nano_graphrag.base import QueryParam
                # mode='global'은 전체 그래프를 탐색하는 모드예요!
                # top_k=20은 상위 20개 엔티티를 찾는 거예요!
                # level=2는 그래프 탐색 깊이예요!
                # mode='local'은 엔티티 기반 검색이에요! community reports 없이도 작동해요!
                # mode='global'은 community reports가 필요해요! (graspologic 필요)
                # top_k는 상위 몇 개의 엔티티를 찾을지 정하는 거예요!
                query_param = QueryParam(
                    mode='local',  # local 모드 사용!
                    top_k=20,
                    level=2
                )
                response = await self.query_rag_api.aquery(question, param=query_param)
                print(f"🔍 [DEBUG] query_rag_api.aquery() 완료!")
                print(f"🔍 [DEBUG] 응답 길이: {len(response) if response else 0}")
                print(f"🔍 [DEBUG] 응답 시작 부분: {response[:100] if response else 'None'}...")
            except Exception as e:
                print(f"❌ [DEBUG] query_rag_api.aquery() 에러: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                raise
        else:
            # LOCAL 모드면 Ollama를 사용해서 답변을 생성해요!
            # 마치 "로컬에서 답하는" 것처럼!
            print(f"💬 질문 모드: Ollama (로컬)")
            # LOCAL 모드 사용 시 Ollama 서버가 실행 중인지 확인해요!
            try:
                import requests
                ollama_check = requests.get("http://localhost:11434/api/tags", timeout=2)
                if ollama_check.status_code != 200:
                    return "❌ Ollama 서버가 실행되지 않았어요! 'ollama serve' 명령어로 서버를 시작해주세요!"
            except:
                return "❌ Ollama 서버에 연결할 수 없어요! 'ollama serve' 명령어로 서버를 시작하거나, 'api' 모드를 사용해주세요!"
            
            print(f"🔍 [DEBUG] query_rag_local.aquery() 호출 시작...")
            try:
                response = await self.query_rag_local.aquery(question)
                print(f"🔍 [DEBUG] query_rag_local.aquery() 완료!")
                print(f"🔍 [DEBUG] 응답 길이: {len(response) if response else 0}")
                print(f"🔍 [DEBUG] 응답 시작 부분: {response[:100] if response else 'None'}...")
            except Exception as e:
                print(f"❌ [DEBUG] query_rag_local.aquery() 에러: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                raise
        
        # 답변이 비어있거나 "Sorry"로 시작하면 경고 메시지 추가해요!
        if not response or response.strip().startswith("Sorry"):
            print("⚠️  그래프에 데이터가 있지만 답변을 생성하지 못했어요.")
            print("💡 더 구체적인 질문을 시도해보세요!")
            print("💡 또는 그래프에 관련 정보가 없을 수 있어요.")
        
        # return은 "이걸 돌려줘"라는 뜻이에요. 답변을 반환해요!
        return response
    
    # get_graph_stats()는 "그래프 통계를 가져오는" 함수예요!
    def get_graph_stats(self) -> dict:
        # networkx는 그래프를 다루는 도구예요!
        import networkx as nx
        
        # graphml_path는 "그래프 파일 경로"예요!
        graphml_path = os.path.join(self.working_dir, "graph_chunk_entity_relation.graphml")
        
        # os.path.exists()는 파일이 있는지 확인하는 거예요!
        if not os.path.exists(graphml_path):
            return {"nodes": 0, "edges": 0, "message": "그래프 파일이 아직 없어요!"}
        
        # nx.read_graphml()은 GraphML 파일을 읽어서 그래프로 만드는 거예요!
        G = nx.read_graphml(graphml_path)
        
        # G.number_of_nodes()는 노드 개수를 세는 거예요!
        # G.number_of_edges()는 엣지 개수를 세는 거예요!
        return {
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "status": "success"
        }

