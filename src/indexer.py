# from은 "가져와"라는 뜻이에요. 다른 곳에 있는 도구를 가져와서 쓸 수 있게 해줘요!
# nano_graphrag는 GraphRAG라는 특별한 도구를 가지고 있는 상자예요
# GraphRAG는 텍스트를 그래프(연결망)로 만들어서 질문에 답할 수 있게 해주는 똑똑한 도구예요!
from nano_graphrag import GraphRAG
# ollama는 로컬 Ollama 서버와 대화할 수 있게 해주는 도구예요!
# 마치 집에 있는 AI 로봇과 대화하는 것처럼!
import ollama
# asyncio는 비동기 프로그래밍을 할 수 있게 해주는 도구예요!
# 마치 여러 일을 동시에 할 수 있게 해주는 것처럼!
import asyncio

# async def는 "비동기 함수"를 만드는 거예요. 마치 "나중에 실행될 함수"를 만드는 것처럼!
# ollama_complete는 Ollama를 사용해서 AI에게 질문하는 함수예요!
# prompt는 "질문 내용"이에요. AI에게 물어볼 내용이에요!
# **kwargs는 "나머지 모든 인자"를 받는 거예요. 마치 "뭐든지 다 받아줄게"라는 뜻이에요!
# 이렇게 하면 nano_graphrag가 추가로 보내는 인자들도 받을 수 있어요!
async def ollama_complete(prompt: str, **kwargs) -> str:
    # ollama.chat()는 Ollama 서버에 메시지를 보내는 거예요!
    # model은 "어떤 AI 모델을 쓸지" 정하는 거예요. "llama3"은 llama3 모델을 사용한다는 뜻이에요!
    # messages는 "대화 내용"이에요. 여기에 질문을 넣어요!
    # role="user"는 "사용자가 말한 것"이라는 뜻이에요!
    # content는 실제 질문 내용이에요!
    response = ollama.chat(
        model="llama3.2:3b",  # llama3.2:3b 모델을 사용해요!
        messages=[{"role": "user", "content": prompt}]
    )
    # response["message"]["content"]는 AI가 답한 내용을 가져오는 거예요!
    # 마치 AI가 답변한 내용을 꺼내는 것처럼!
    return response["message"]["content"]

# NanoGraphRAG 설정 (로컬 Ollama 연결)
# GraphRAG()는 함수를 호출하는 거예요. 마치 "도구를 준비해줘"라고 말하는 것처럼!
# working_dir은 "작업할 폴더"를 지정하는 거예요. 그래프 데이터를 저장할 곳이에요!
# "./graph_storage"는 현재 폴더 안에 있는 graph_storage라는 폴더를 의미해요!
# best_model_func은 "주요 작업에 쓸 AI 함수"를 지정하는 거예요!
# ollama_complete는 우리가 만든 Ollama 함수예요!
# cheap_model_func은 "간단한 작업에 쓸 AI 함수"를 지정하는 거예요!
# 같은 함수를 써도 괜찮아요!
rag = GraphRAG(
    working_dir="./graph_storage",
    best_model_func=ollama_complete,  # Ollama 함수를 사용한다는 뜻이에요!
    cheap_model_func=ollama_complete,  # 간단한 작업에도 Ollama 함수를 써요!
)

# 1. 아까 뽑은 텍스트 읽기
# with open()은 파일을 여는 거예요. 마치 공책을 펼치는 것처럼!
# "r"은 "읽기 모드"예요. 파일을 읽을 수 있다는 뜻이에요!
# f는 파일을 가리키는 손잡이 같은 거예요!
with open("data/sample_report.txt", "r", encoding="utf-8") as f:
    # f.read()는 파일 전체를 읽어오는 거예요. 마치 공책 전체를 한 번에 읽는 것처럼!
    # content 상자에 읽은 내용을 담아요!
    content = f.read()

# 2. 인덱싱 (그래프 만들기)
# rag.insert()는 텍스트를 그래프로 만드는 거예요!
# 마치 책의 내용을 지도처럼 연결해서 정리하는 것과 같아요!
# insert는 "넣어"라는 뜻이에요. 텍스트를 그래프 안에 넣는 거예요!
rag.insert(content)

# 3. 질문해보기
# rag.query()는 질문을 하면 답을 찾아주는 거예요!
# 마치 책을 읽고 질문하면 답을 찾아주는 똑똑한 도서관 사서 같은 거예요!
# print()는 화면에 결과를 출력하는 거예요. 마치 말하는 것처럼!
print(rag.query("what is the Gross margin in the third quarter of fiscal 2026?"))