import os
import sys

# Streamlit은 웹 UI를 쉽게 만드는 도구예요!
# 마치 파이썬으로 파워포인트 + 웹페이지를 섞어서 만드는 느낌이에요!
import streamlit as st

# requests는 다른 서버(FastAPI)에 HTTP 요청을 보내는 도구예요!
# 마치 "택배를 보내고, 답장을 받는 우체국" 같은 역할이에요!
import requests

# 현재 파일(src 폴더) 경로를 파이썬 모듈 경로에 추가해요
# 이렇게 하면 parser.py 같은 걸 import 할 수 있어요!
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from parser import extract_text_from_pdf  # PDF -> 텍스트 함수


# -------------------------------
# 1. 기본 설정 (페이지 레이아웃)
# -------------------------------

# 페이지 제목과 레이아웃을 설정해요
st.set_page_config(
    page_title="Financial GraphRAG UI",
    layout="wide",  # wide는 화면을 가로로 넓게 쓰겠다는 뜻이에요!
)

# 세션 상태에 채팅 내역 저장 상자를 하나 만들어요
if "messages" not in st.session_state:
    # messages는 채팅 기록이 들어갈 리스트예요!
    # 각 원소는 {"role": "user" or "assistant", "content": "..."} 이런 딕셔너리예요!
    st.session_state["messages"] = []


# -------------------------------
# 2. 사이드바: PDF 업로드 & 인덱싱
# -------------------------------

with st.sidebar:
    st.title("📄 PDF 인덱싱")

    # FastAPI 서버 주소예요
    # 만약 포트를 바꾸면 여기만 수정하면 돼요!
    api_base = "http://localhost:8000"

    # PDF 업로드 위젯이에요
    uploaded_pdf = st.file_uploader("PDF 파일 올리기", type=["pdf"])

    # "PDF → 텍스트 추출 + 인덱싱" 버튼
    if st.button("📚 이 PDF로 그래프 인덱싱하기", type="primary"):
        if uploaded_pdf is None:
            st.error("먼저 PDF 파일을 올려주세요!")
        else:
            try:
                # 업로드된 파일을 임시 경로에 저장해요
                tmp_path = os.path.join(BASE_DIR, "_uploaded_temp.pdf")
                with open(tmp_path, "wb") as tmp_f:
                    tmp_f.write(uploaded_pdf.read())

                # parser.extract_text_from_pdf로 텍스트를 뽑아요
                st.info("PDF에서 텍스트 추출 중... (조금만 기다려주세요)")
                text = extract_text_from_pdf(tmp_path)

                # FastAPI /insert로 텍스트를 보내요
                st.info("GraphRAG에 텍스트 인덱싱 중... (조금 시간이 걸릴 수 있어요)")
                resp = requests.post(
                    f"{api_base}/insert",
                    json={"text": text},
                    timeout=120,
                )

                if resp.status_code == 200:
                    st.success("✅ 인덱싱 완료! 이제 질문할 수 있어요.")
                else:
                    st.error(f"❌ 인덱싱 실패: {resp.status_code} - {resp.text}")

            except Exception as e:
                st.error(f"❌ 에러 발생: {e}")

    st.markdown("---")

    # 그래프 현황판: FastAPI에 간단한 통계를 물어볼 거예요
    st.subheader("📊 그래프 현황")
    try:
        stats_resp = requests.get(f"{api_base}/graph_stats", timeout=5)
        if stats_resp.status_code == 200:
            data = stats_resp.json()
            st.write(f"노드 수: **{data.get('nodes', 0)}**")
            st.write(f"엣지 수: **{data.get('edges', 0)}**")
        else:
            st.write("그래프 정보를 가져올 수 없어요.")
    except Exception:
        st.write("FastAPI 서버가 아직 안 켜졌을 수도 있어요.")


# -------------------------------
# 3. 중앙: 채팅 UI (질문/답변)
# -------------------------------

st.title("💬 Financial GraphRAG 챗봇")
st.caption("왼쪽에서 PDF를 인덱싱한 후, 여기서 자연어로 질문해보세요!")

# 지금까지의 메시지를 위에서부터 순서대로 보여줘요
for msg in st.session_state["messages"]:
    role = "👤 사용자" if msg["role"] == "user" else "🤖 GraphRAG"
    with st.chat_message(msg["role"]):
        st.markdown(f"**{role}**\n\n{msg['content']}")

# 새 질문 입력창 (Streamlit의 chat_input은 Enter 치면 바로 전송돼요)
user_input = st.chat_input("엔비디아에 대해 뭐가 궁금해? (예: What is NVIDIA's revenue?)")

if user_input:
    # 1) 화면에 사용자 메시지 추가
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f"**👤 사용자**\n\n{user_input}")

    # 2) FastAPI /query에 질문 보내기
    try:
        with st.chat_message("assistant"):
            with st.spinner("생각 중이에요... (Ollama + GraphRAG 호출 중)"):
                resp = requests.post(
                    f"{api_base}/query",
                    json={"question": user_input},
                    timeout=120,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data.get("answer", "(no answer)")
                    st.markdown(f"**🤖 GraphRAG**\n\n{answer}")
                    # 세션에도 저장
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": answer}
                    )
                else:
                    err = f"❌ 오류: {resp.status_code} - {resp.text}"
                    st.error(err)
                    st.session_state["messages"].append(
                        {"role": "assistant", "content": err}
                    )
    except Exception as e:
        err = f"❌ 서버 연결 에러: {e}"
        st.error(err)
        st.session_state["messages"].append(
            {"role": "assistant", "content": err}
        )


