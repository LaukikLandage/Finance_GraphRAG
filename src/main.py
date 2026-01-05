import asyncio
from nano_graphrag import GraphRAG
from ollama import AsyncClient

# --- [1] Ollama와 대화하는 함수 (LLM) ---
async def ollama_model_if(prompt, system_prompt=None, history_messages=[], **kwargs):
    client = AsyncClient()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})
    
    # llama3.2:3b 모델을 사용해요!
    # model은 "어떤 AI 모델을 쓸지" 정하는 거예요!
    response = await client.chat(model="llama3.2:3b", messages=messages)
    return response['message']['content']

# --- [2] 텍스트를 숫자로 변환하는 함수 (Embedding) ---
# async def는 "비동기 함수"를 만드는 거예요. 마치 "나중에 실행될 함수"를 만드는 것처럼!
# ollama_embedding_if는 텍스트를 숫자 벡터로 바꾸는 함수예요!
# texts는 "텍스트들의 리스트"예요. 여러 텍스트를 한 번에 변환할 수 있어요!
async def ollama_embedding_if(texts):
    # AsyncClient()는 Ollama 서버와 비동기로 대화할 수 있는 클라이언트예요!
    # 마치 전화기를 만드는 것처럼!
    client = AsyncClient()
    # embeds는 "변환된 숫자 벡터들을 담을 상자"예요!
    embeds = []
    # for는 반복문이에요. texts 안에 있는 각 text를 하나씩 꺼내서 반복하는 거예요!
    for text in texts:
        # client.embeddings()는 텍스트를 숫자 벡터로 변환하는 거예요!
        # model="nomic-embed-text"는 "nomic-embed-text" 모델을 사용한다는 뜻이에요!
        # prompt=text는 변환할 텍스트예요!
        response = await client.embeddings(model="nomic-embed-text", prompt=text)
        # response['embedding']은 변환된 숫자 벡터예요!
        # embeds.append()는 embeds 상자에 숫자 벡터를 넣는 거예요!
        embeds.append(response['embedding'])
    # return은 "이걸 돌려줘"라는 뜻이에요. 변환된 벡터들을 반환해요!
    return embeds

# embedding_dim은 "숫자 벡터의 크기"예요!
# nomic-embed-text 모델은 768차원 벡터를 만들어요!
# 마치 "이 함수가 만드는 숫자 벡터는 768개의 숫자로 이루어져 있어요!"라는 뜻이에요!
ollama_embedding_if.embedding_dim = 768

# --- [3] 실제 실행 부분 ---
async def main():
    # 그래프 데이터가 저장될 폴더
    graph_func = GraphRAG(
        working_dir="./my_graph_data",
        best_model_func=ollama_model_if,   # 뇌 연결
        cheap_model_func=ollama_model_if,  # 보조 뇌 연결
        embedding_func=ollama_embedding_if # 눈 연결
    )

    # 샘플 데이터 입력 (금융 보고서 텍스트라고 가정)
    # text는 "입력할 텍스트"예요. 그래프로 만들 텍스트를 담아요!
    text = "VIK AI는 M1 맥북에서 돌아가는 보안 금융 분석 에이전트입니다. NanoGraphRAG를 엔진으로 사용합니다."
    
    # print()는 화면에 글자를 출력하는 거예요. 마치 말하는 것처럼!
    print("📊 지식 그래프 만드는 중...")
    # graph_func.ainsert()는 비동기로 텍스트를 그래프에 넣는 거예요!
    # await는 "이게 끝날 때까지 기다려"라는 뜻이에요!
    await graph_func.ainsert(text)
    
    # 질문 던지기
    # print()로 질문을 출력해요!
    print("\n🔍 질문: VIK AI가 사용하는 엔진은 뭐야?")
    # graph_func.aquery()는 비동기로 질문에 답을 찾는 거예요!
    # await는 "답변이 올 때까지 기다려"라는 뜻이에요!
    response = await graph_func.aquery("VIK AI가 사용하는 엔진은 뭐야?")
    # f"..."는 f-string이라고 해요. 변수를 문자열 안에 넣을 수 있어요!
    # 마치 "답변: {response}"에서 {response} 부분이 실제 답변으로 바뀌는 거예요!
    print(f"🤖 답변: {response}")

if __name__ == "__main__":
    asyncio.run(main())