import asyncio
import os
from nano_graphrag import GraphRAG
from ollama import AsyncClient

# --- [1] Ollama와 대화하는 함수 (LLM) ---
# async def는 "비동기 함수"를 만드는 거예요. 마치 "나중에 실행될 함수"를 만드는 것처럼!
# ollama_model_if는 Ollama를 사용해서 AI에게 질문하는 함수예요!
# prompt는 "질문 내용"이에요. AI에게 물어볼 내용이에요!
# **kwargs는 "나머지 모든 인자"를 받는 거예요. 마치 "뭐든지 다 받아줄게"라는 뜻이에요!
async def ollama_model_if(prompt, system_prompt=None, history_messages=[], **kwargs):
    # AsyncClient()는 Ollama 서버와 비동기로 대화할 수 있는 클라이언트예요!
    # 마치 전화기를 만드는 것처럼!
    client = AsyncClient()
    # messages는 "대화 내용을 담을 상자"예요!
    messages = []
    # if는 "만약"이라는 뜻이에요!
    # system_prompt가 있으면 시스템 메시지를 추가해요!
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    # history_messages는 "이전 대화 내용"이에요!
    messages.extend(history_messages)
    # 사용자의 질문을 추가해요!
    messages.append({"role": "user", "content": prompt})
    
    # llama3.2:3b 모델을 사용해요!
    # model은 "어떤 AI 모델을 쓸지" 정하는 거예요!
    response = await client.chat(model="llama3.2:3b", messages=messages)
    # response['message']['content']는 AI가 답한 내용을 가져오는 거예요!
    # 마치 AI가 답변한 내용을 꺼내는 것처럼!
    return response['message']['content']

# --- [2] 텍스트를 숫자로 변환하는 함수 (Embedding) ---
# ollama_embedding_if는 텍스트를 숫자 벡터로 바꾸는 함수예요!
# texts는 "텍스트들의 리스트"예요. 여러 텍스트를 한 번에 변환할 수 있어요!
async def ollama_embedding_if(texts):
    # AsyncClient()는 Ollama 서버와 비동기로 대화할 수 있는 클라이언트예요!
    client = AsyncClient()
    # embeds는 "변환된 숫자 벡터들을 담을 상자"예요!
    embeds = []
    # for는 반복문이에요. texts 안에 있는 각 text를 하나씩 꺼내서 반복하는 거예요!
    for text in texts:
        # client.embeddings()는 텍스트를 숫자 벡터로 변환하는 거예요!
        # model="nomic-embed-text"는 "nomic-embed-text" 모델을 사용한다는 뜻이에요!
        response = await client.embeddings(model="nomic-embed-text", prompt=text)
        # response['embedding']은 변환된 숫자 벡터예요!
        # embeds.append()는 embeds 상자에 숫자 벡터를 넣는 거예요!
        embeds.append(response['embedding'])
    # return은 "이걸 돌려줘"라는 뜻이에요. 변환된 벡터들을 반환해요!
    return embeds

# embedding_dim은 "숫자 벡터의 크기"예요!
# nomic-embed-text 모델은 768차원 벡터를 만들어요!
ollama_embedding_if.embedding_dim = 768

async def main():
    # 개발 모드 설정
    # DEV_MODE가 True면 앞 50줄만 사용해서 빠르게 테스트해요!
    # False면 전체 문서를 사용해서 제대로 학습해요!
    DEV_MODE = False  # 개발할 때는 True로 바꿔요!
    
    # 1. 그래프 데이터 폴더 설정
    # 중요: API로 새로 학습시키려면 기존 폴더를 지우거나 이름을 바꿔주세요!
    WORKING_DIR = "./graph_storage_api" 
    if not os.path.exists(WORKING_DIR):
        os.mkdir(WORKING_DIR)

    # 2. NanoGraphRAG 초기화 (Ollama 사용 모드)
    # best_model_func은 "주요 작업에 쓸 AI 함수"를 지정하는 거예요!
    # cheap_model_func은 "간단한 작업에 쓸 AI 함수"를 지정하는 거예요!
    # embedding_func은 "텍스트를 숫자로 변환하는 함수"예요!
    rag = GraphRAG(
        working_dir=WORKING_DIR,
        best_model_func=ollama_model_if,   # Ollama 함수를 사용한다는 뜻이에요!
        cheap_model_func=ollama_model_if,  # 간단한 작업에도 Ollama 함수를 써요!
        embedding_func=ollama_embedding_if # Embedding 함수를 연결해요!
    )

    # 3. PDF에서 추출한 텍스트 읽기
    # with open()은 파일을 여는 거예요. 마치 공책을 펼치는 것처럼!
    # "r"은 "읽기 모드"예요. 파일을 읽을 수 있다는 뜻이에요!
    # encoding="utf-8"은 한글도 제대로 읽을 수 있게 해주는 거예요!
    print("PDF 텍스트 파일 읽는 중...")
    with open("data/sample_report.txt", "r", encoding="utf-8") as f:
        if DEV_MODE:
            # 개발 모드: 앞 50줄만 사용 (빠른 테스트용!)
            # 마치 "책의 앞부분만 읽어서 연습하는" 것처럼!
            lines = []
            for i, line in enumerate(f):
                if i >= 50:  # 50줄까지만 읽어요!
                    break
                lines.append(line)
            content = "".join(lines)
            print(f"개발 모드: 앞 {len(lines)}줄만 사용해요!")
        else:
            # 실전 모드: 전체 문서 사용
            # f.read()는 파일 전체를 읽어오는 거예요. 마치 공책 전체를 한 번에 읽는 것처럼!
            content = f.read()
            print(f"실전 모드: 전체 문서 사용 ({len(content)} 글자)")

    # 4. 인덱싱 (공부 시작!)
    # rag.ainsert()는 비동기로 텍스트를 그래프에 넣는 거예요!
    # await는 "이게 끝날 때까지 기다려"라는 뜻이에요!
    print("🚀 Ollama를 사용하여 지식 그래프 구축 시작... (시간이 좀 걸릴 수 있어요!)")
    await rag.ainsert(content)
    print("✅ 구축 완료!")

    # 5. 질문하기
    # rag.aquery()는 비동기로 질문에 답을 찾는 거예요!
    query = "What is NVIDIA's revenue?"
    print(f"\n❓ 질문: {query}")
    response = await rag.aquery(query)
    print(f"\n🤖 답변: {response}")

if __name__ == "__main__":
    asyncio.run(main())