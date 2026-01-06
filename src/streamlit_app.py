import streamlit as st
import requests
import sys
import os
import streamlit.components.v1 as components
import time
import json
from datetime import datetime

# 현재 파일의 폴더 경로를 추가해요!
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 페이지 설정
st.set_page_config(
    page_title="VIK AI GraphRAG",
    page_icon="🤖",
    layout="wide"
)

# 데이터 소스 관리 파일 경로
DATA_SOURCES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data_sources.json")

# 데이터 소스 로드 함수
def load_data_sources():
    if os.path.exists(DATA_SOURCES_FILE):
        with open(DATA_SOURCES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"pdfs": [], "urls": [], "texts": []}

# 데이터 소스 저장 함수
def save_data_sources(data_sources):
    with open(DATA_SOURCES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_sources, f, ensure_ascii=False, indent=2)

# 데이터 소스 추가 함수
def add_data_source(source_type, name, content_preview=""):
    data_sources = load_data_sources()
    source = {
        "name": name,
        "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "content_preview": content_preview[:100] + "..." if len(content_preview) > 100 else content_preview
    }
    data_sources[source_type].append(source)
    save_data_sources(data_sources)

# 데이터 소스 삭제 함수
def delete_data_source(source_type, index):
    data_sources = load_data_sources()
    if 0 <= index < len(data_sources[source_type]):
        del data_sources[source_type][index]
        save_data_sources(data_sources)
        return True
    return False

# 제목
st.title("🤖 VIK AI: Financial GraphRAG")
st.markdown("금융 보고서를 분석하는 GraphRAG 시스템이에요!")

# API 엔드포인트
API_BASE_URL = "http://127.0.0.1:8000"

# 사이드바
with st.sidebar:
    st.header("📊 시스템 상태")
    
    # 서버 상태 확인
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ 서버 연결됨")
            server_connected = True
        else:
            st.error("❌ 서버 응답 오류")
            server_connected = False
    except:
        st.error("❌ 서버 연결 실패")
        server_connected = False
    
    # 그래프 통계
    try:
        response = requests.get(f"{API_BASE_URL}/graph_stats", timeout=2)
        if response.status_code == 200:
            stats = response.json()
            st.metric("노드 수", stats.get("nodes", 0))
            st.metric("엣지 수", stats.get("edges", 0))
    except:
        st.warning("⚠️ 그래프 통계를 가져올 수 없어요")
    
    st.divider()
    
    # 모드 선택
    st.header("⚙️ 설정")
    query_mode = st.radio(
        "질문 모드 선택",
        options=["api", "local"],
        format_func=lambda x: "🌐 OpenAI API (정확)" if x == "api" else "💻 Ollama 로컬 (빠름)",
        help="API 모드는 OpenAI를 사용하고, Local 모드는 Ollama를 사용해요!"
    )
    
    if query_mode == "api":
        st.info("💡 OpenAI API를 사용해요. 더 정확하지만 유료예요.")
    else:
        st.info("💡 Ollama 로컬 모델을 사용해요. 무료지만 Ollama 서버가 실행 중이어야 해요!")
    
    st.divider()
    
    # 그래프 시각화 새로고침 버튼
    st.header("🎨 그래프 시각화")
    if st.button("🔄 그래프 새로고침", use_container_width=True):
        st.rerun()

# 메인 영역
tab1, tab2, tab3, tab4 = st.tabs(["💬 질문하기", "📝 데이터 추가", "🎨 그래프 시각화", "📚 데이터 목록"])

# 탭 1: 질문하기
with tab1:
    st.header("💬 질문하기")
    
    # 질문 입력
    question = st.text_input(
        "질문을 입력하세요",
        placeholder="예: What is NVIDIA's revenue?",
        key="question_input"
    )
    
    # 질문 버튼
    if st.button("🔍 질문하기", type="primary", use_container_width=True):
        if not question:
            st.warning("⚠️ 질문을 입력해주세요!")
        else:
            with st.spinner(f"🤔 답변 생성 중... ({query_mode} 모드)"):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/query",
                        json={
                            "question": question,
                            "mode": query_mode  # 선택한 모드 사용!
                        },
                        timeout=120
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ 답변 완료! ({result.get('mode', 'unknown')} 모드)")
                        
                        # 답변 표시
                        st.markdown("### 🤖 AI의 답변")
                        st.markdown(result.get("answer", "답변을 생성할 수 없어요."))
                    else:
                        st.error(f"❌ 에러: {response.status_code}")
                        st.error(response.text)
                        
                except Exception as e:
                    st.error(f"❌ 에러 발생: {str(e)}")

# 탭 2: 텍스트 추가
with tab2:
    st.header("📝 데이터 추가")
    
    # 입력 방법 선택
    input_method = st.radio(
        "입력 방법 선택",
        options=["텍스트 직접 입력", "PDF 업로드", "URL 크롤링"],
        horizontal=True
    )
    
    # 1. 텍스트 직접 입력
    if input_method == "텍스트 직접 입력":
        text_input = st.text_area(
            "인덱싱할 텍스트를 입력하세요",
            placeholder="예: NVIDIA reported revenue of $57.0 billion...",
            height=200,
            key="text_input"
        )
        
        if st.button("📚 텍스트 추가하기", type="primary", use_container_width=True):
            if not text_input:
                st.warning("⚠️ 텍스트를 입력해주세요!")
            else:
                with st.spinner("📚 인덱싱 중... (시간이 걸릴 수 있어요)"):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/insert",
                            json={"text": text_input},
                            timeout=300
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success("✅ 인덱싱 완료!")
                            
                            # 데이터 소스 기록
                            add_data_source("texts", "텍스트 입력", text_input)
                            
                            # 그래프 자동 재생성
                            with st.spinner("🎨 그래프 재생성 중..."):
                                import subprocess
                                project_root = os.path.dirname(os.path.dirname(__file__))
                                result = subprocess.run(
                                    ["python3", "src/visualize.py"],
                                    capture_output=True,
                                    text=True,
                                    cwd=project_root
                                )
                                if result.returncode == 0:
                                    st.success("✅ 그래프가 업데이트되었어요!")
                                    # 파일 수정 시간 강제 업데이트
                                    graph_html_path = os.path.join(project_root, "graph_ui.html")
                                    if os.path.exists(graph_html_path):
                                        os.utime(graph_html_path, None)
                                    # 세션 상태 초기화
                                    st.session_state.last_graph_mtime = 0
                                    st.info("💡 '그래프 시각화' 탭을 클릭하면 새 그래프를 볼 수 있어요!")
                                else:
                                    st.warning(f"⚠️ 그래프 재생성 실패: {result.stderr}")
                        else:
                            st.error(f"❌ 에러: {response.status_code}")
                            st.error(response.text)
                            
                    except Exception as e:
                        st.error(f"❌ 에러 발생: {str(e)}")
    
    # 2. PDF 업로드
    elif input_method == "PDF 업로드":
        uploaded_file = st.file_uploader(
            "PDF 파일을 업로드하세요",
            type=["pdf"],
            key="pdf_uploader"
        )
        
        if st.button("📄 PDF 추가하기", type="primary", use_container_width=True):
            if not uploaded_file:
                st.warning("⚠️ PDF 파일을 업로드해주세요!")
            else:
                with st.spinner("📄 PDF 처리 중..."):
                    try:
                        # 파일명 안전하게 처리
                        safe_filename = uploaded_file.name if uploaded_file.name else "uploaded.pdf"
                        safe_filename = safe_filename.replace(" ", "_")  # 공백 제거
                        
                        # PDF 파일을 임시로 저장
                        temp_pdf_path = os.path.join(
                            os.path.dirname(os.path.dirname(__file__)),  # 프로젝트 루트 디렉토리
                            f"temp_{safe_filename}"
                        )
                        
                        st.info(f"📝 파일명: {safe_filename}")
                        
                        with open(temp_pdf_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        st.info(f"✅ 파일 저장 완료: {temp_pdf_path}")
                        
                        # PDF에서 텍스트 추출
                        from parser import extract_text_from_pdf
                        text = extract_text_from_pdf(temp_pdf_path)
                        
                        st.info(f"📝 추출된 텍스트: {len(text)} 글자")
                        
                        # 임시 파일 삭제
                        if os.path.exists(temp_pdf_path):
                            os.remove(temp_pdf_path)
                            st.info(f"🗑️ 임시 파일 삭제 완료")
                        
                        # 그래프 자동 초기화 (PDF 추가 시마다 새로 시작)
                        with st.spinner("🔄 그래프 초기화 중... (기존 데이터 백업 중)"):
                            try:
                                reset_response = requests.post(
                                    f"{API_BASE_URL}/reset",
                                    timeout=30
                                )
                                if reset_response.status_code == 200:
                                    reset_result = reset_response.json()
                                    st.success("✅ 그래프 초기화 완료!")
                                    if reset_result.get("backup_dir"):
                                        st.info(f"💾 기존 그래프 백업: {reset_result.get('backup_dir')}")
                                else:
                                    st.warning(f"⚠️ 그래프 초기화 실패: {reset_response.status_code}")
                                    st.info("💡 기존 그래프에 추가로 진행합니다...")
                            except Exception as e:
                                st.warning(f"⚠️ 그래프 초기화 중 에러: {str(e)}")
                                st.info("💡 기존 그래프에 추가로 진행합니다...")
                        
                        # 인덱싱
                        with st.spinner("📚 인덱싱 중..."):
                            response = requests.post(
                                f"{API_BASE_URL}/insert",
                                json={"text": text},
                                timeout=300
                            )
                            
                            if response.status_code == 200:
                                st.success("✅ PDF 인덱싱 완료!")
                                
                                # 데이터 소스 기록
                                add_data_source("pdfs", safe_filename, text)
                                
                                # 그래프 자동 재생성
                                with st.spinner("🎨 그래프 재생성 중..."):
                                    import subprocess
                                    project_root = os.path.dirname(os.path.dirname(__file__))
                                    result = subprocess.run(
                                        ["python3", "src/visualize.py"],
                                        capture_output=True,
                                        text=True,
                                        cwd=project_root
                                    )
                                    
                                    st.info(f"📊 그래프 재생성 결과: returncode={result.returncode}")
                                    if result.stdout:
                                        st.text(f"출력: {result.stdout[-200:]}")  # 마지막 200자만
                                    
                                    if result.returncode == 0:
                                        st.success("✅ 그래프가 업데이트되었어요!")
                                        st.info("💡 '그래프 시각화' 탭에서 확인하세요!")
                                        # 파일 수정 시간 강제 업데이트
                                        graph_html_path = os.path.join(project_root, "graph_ui.html")
                                        if os.path.exists(graph_html_path):
                                            # 파일 수정 시간 업데이트
                                            os.utime(graph_html_path, None)
                                            st.success(f"✅ 그래프 파일 타임스탬프 업데이트!")
                                        # 세션 상태 초기화하여 강제 새로고침
                                        st.session_state.last_graph_mtime = 0
                                        st.rerun()  # 페이지 새로고침
                                    else:
                                        st.warning(f"⚠️ 그래프 재생성 실패")
                                        if result.stderr:
                                            st.error(f"에러: {result.stderr}")
                            else:
                                st.error(f"❌ 에러: {response.status_code}")
                                st.error(response.text)
                                
                    except Exception as e:
                        st.error(f"❌ 에러 발생: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
                        # 에러 시에도 임시 파일 삭제
                        if 'temp_pdf_path' in locals() and os.path.exists(temp_pdf_path):
                            os.remove(temp_pdf_path)
    
    # 3. URL 크롤링
    elif input_method == "URL 크롤링":
        url_input = st.text_input(
            "크롤링할 URL을 입력하세요",
            placeholder="예: https://www.example.com/news",
            key="url_input"
        )
        
        if st.button("🌐 URL 추가하기", type="primary", use_container_width=True):
            if not url_input:
                st.warning("⚠️ URL을 입력해주세요!")
            else:
                with st.spinner("🌐 웹 페이지 크롤링 중..."):
                    try:
                        # URL 크롤링 및 인덱싱
                        from url import auto_researcher
                        
                        # auto_researcher 함수 호출
                        result = auto_researcher(url_input)
                        
                        if result.get("status") == "success":
                            st.success("✅ URL 크롤링 및 인덱싱 완료!")
                            
                            # 데이터 소스 기록
                            add_data_source("urls", url_input, result.get("text", "")[:100])
                            
                            # 그래프 자동 재생성
                            with st.spinner("🎨 그래프 재생성 중..."):
                                import subprocess
                                result_viz = subprocess.run(
                                    ["python3", "src/visualize.py"],
                                    capture_output=True,
                                    text=True,
                                    cwd=os.path.dirname(os.path.dirname(__file__))
                                )
                                if result_viz.returncode == 0:
                                    st.success("✅ 그래프가 업데이트되었어요!")
                                    # 파일 수정 시간 강제 업데이트
                                    project_root = os.path.dirname(os.path.dirname(__file__))
                                    graph_html_path = os.path.join(project_root, "graph_ui.html")
                                    if os.path.exists(graph_html_path):
                                        os.utime(graph_html_path, None)
                                    # 세션 상태 초기화
                                    st.session_state.last_graph_mtime = 0
                                    st.info("💡 '그래프 시각화' 탭을 클릭하면 새 그래프를 볼 수 있어요!")
                                else:
                                    st.warning(f"⚠️ 그래프 재생성 실패: {result_viz.stderr}")
                        else:
                            st.error(f"❌ 에러: {result.get('error', '알 수 없는 오류')}")
                            
                    except Exception as e:
                        st.error(f"❌ 에러 발생: {str(e)}")

# 탭 3: 그래프 시각화
with tab3:
    st.header("🎨 그래프 시각화")
    
    # 그래프 시각화 설명
    st.markdown("""
    현재 그래프의 구조를 인터랙티브하게 확인할 수 있어요!
    - 노드를 드래그해서 이동할 수 있어요
    - 마우스 휠로 확대/축소할 수 있어요
    - 노드를 클릭하면 연결된 노드가 하이라이트돼요
    """)
    
    # 그래프 파일 경로
    graph_html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "graph_ui.html")
    
    # 그래프 파일이 있는지 확인
    if os.path.exists(graph_html_path):
        # 파일 수정 시간 확인
        file_mtime = os.path.getmtime(graph_html_path)
        file_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_mtime))
        
        # 세션 상태에 마지막 확인 시간 저장
        if 'last_graph_mtime' not in st.session_state:
            st.session_state.last_graph_mtime = 0
        
        # 파일이 업데이트되었는지 확인
        graph_updated = file_mtime > st.session_state.last_graph_mtime
        if graph_updated:
            st.session_state.last_graph_mtime = file_mtime
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📅 마지막 업데이트: {file_time}")
            if graph_updated:
                st.success("✨ 그래프가 업데이트되었어요!")
        with col2:
            if st.button("🔄 새로고침", key="refresh_graph"):
                st.session_state.last_graph_mtime = 0
                st.rerun()
        
        # HTML 파일 읽기 (파일 수정 시간을 해시로 사용하여 캐시 무효화)
        with open(graph_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 그래프 표시 (파일 수정 시간을 URL 파라미터로 추가하여 브라우저 캐시 무효화)
        # iframe의 src에 타임스탬프를 추가하는 방식으로 강제 새로고침
        import hashlib
        content_hash = hashlib.md5(html_content.encode()).hexdigest()[:8]
        
        # HTML 내용에 타임스탬프 메타 태그 추가
        if '<head>' in html_content:
            timestamp_meta = f'<meta name="cache-control" content="no-cache, no-store, must-revalidate"><meta name="timestamp" content="{file_mtime}">'
            html_content = html_content.replace('<head>', f'<head>{timestamp_meta}')
        
        # 그래프 표시
        components.html(html_content, height=800, scrolling=True)
        
        st.divider()
        
        # 그래프 재생성 버튼
        st.markdown("### 🔧 그래프 관리")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎨 그래프 재생성", use_container_width=True):
                with st.spinner("그래프 생성 중..."):
                    try:
                        # visualize.py 실행
                        import subprocess
                        result = subprocess.run(
                            ["python3", "src/visualize.py"],
                            capture_output=True,
                            text=True,
                            cwd=os.path.dirname(os.path.dirname(__file__))
                        )
                        
                        if result.returncode == 0:
                            st.success("✅ 그래프가 재생성되었어요!")
                            time.sleep(1)  # 파일 쓰기 완료 대기
                            st.rerun()
                        else:
                            st.error(f"❌ 에러: {result.stderr}")
                    except Exception as e:
                        st.error(f"❌ 에러 발생: {str(e)}")
        
        with col2:
            if st.button("📊 그래프 통계 보기", use_container_width=True):
                try:
                    response = requests.get(f"{API_BASE_URL}/graph_stats", timeout=2)
                    if response.status_code == 200:
                        stats = response.json()
                        st.json(stats)
                except Exception as e:
                    st.error(f"❌ 에러: {str(e)}")
    else:
        st.warning("⚠️ 그래프 파일을 찾을 수 없어요!")
        st.info(f"경로: {graph_html_path}")
        
        # 그래프 생성 버튼
        if st.button("🎨 그래프 생성하기", type="primary", use_container_width=True):
            with st.spinner("그래프 생성 중..."):
                try:
                    # visualize.py 실행
                    import subprocess
                    result = subprocess.run(
                        ["python3", "src/visualize.py"],
                        capture_output=True,
                        text=True,
                        cwd=os.path.dirname(os.path.dirname(__file__))
                    )
                    
                    if result.returncode == 0:
                        st.success("✅ 그래프가 생성되었어요!")
                        time.sleep(1)  # 파일 쓰기 완료 대기
                        st.rerun()
                    else:
                        st.error(f"❌ 에러: {result.stderr}")
                        st.code(result.stdout)
                except Exception as e:
                    st.error(f"❌ 에러 발생: {str(e)}")

# 탭 4: 데이터 목록
with tab4:
    st.header("📚 데이터 소스 목록")
    
    st.markdown("""
    지금까지 추가한 PDF, URL, 텍스트 목록을 확인하고 관리할 수 있어요!
    """)
    
    # 데이터 소스 로드
    data_sources = load_data_sources()
    
    # PDF 목록
    st.subheader("📄 PDF 파일")
    if data_sources["pdfs"]:
        for idx, pdf in enumerate(data_sources["pdfs"]):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{pdf['name']}**")
            with col2:
                st.caption(f"추가: {pdf['added_at']}")
            with col3:
                if st.button("🗑️ 삭제", key=f"delete_pdf_{idx}"):
                    if delete_data_source("pdfs", idx):
                        st.success("✅ 삭제되었어요!")
                        st.rerun()
            
            # 내용 미리보기
            with st.expander("📝 내용 미리보기"):
                st.text(pdf.get('content_preview', '미리보기 없음'))
            
            st.divider()
    else:
        st.info("아직 추가된 PDF가 없어요!")
    
    # URL 목록
    st.subheader("🌐 URL")
    if data_sources["urls"]:
        for idx, url in enumerate(data_sources["urls"]):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{url['name']}**")
            with col2:
                st.caption(f"추가: {url['added_at']}")
            with col3:
                if st.button("🗑️ 삭제", key=f"delete_url_{idx}"):
                    if delete_data_source("urls", idx):
                        st.success("✅ 삭제되었어요!")
                        st.rerun()
            
            # 내용 미리보기
            with st.expander("📝 내용 미리보기"):
                st.text(url.get('content_preview', '미리보기 없음'))
            
            st.divider()
    else:
        st.info("아직 추가된 URL이 없어요!")
    
    # 텍스트 목록
    st.subheader("📝 텍스트")
    if data_sources["texts"]:
        for idx, text in enumerate(data_sources["texts"]):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{text['name']}**")
            with col2:
                st.caption(f"추가: {text['added_at']}")
            with col3:
                if st.button("🗑️ 삭제", key=f"delete_text_{idx}"):
                    if delete_data_source("texts", idx):
                        st.success("✅ 삭제되었어요!")
                        st.rerun()
            
            # 내용 미리보기
            with st.expander("📝 내용 미리보기"):
                st.text(text.get('content_preview', '미리보기 없음'))
            
            st.divider()
    else:
        st.info("아직 추가된 텍스트가 없어요!")
    
    # 전체 통계
    st.divider()
    st.subheader("📊 전체 통계")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 PDF", len(data_sources["pdfs"]))
    with col2:
        st.metric("🌐 URL", len(data_sources["urls"]))
    with col3:
        st.metric("📝 텍스트", len(data_sources["texts"]))
    
    # 전체 삭제 버튼
    st.divider()
    st.warning("⚠️ 주의: 아래 버튼은 모든 데이터 소스 기록을 삭제해요! (그래프 데이터는 유지돼요)")
    if st.button("🗑️ 전체 기록 삭제", type="secondary"):
        save_data_sources({"pdfs": [], "urls": [], "texts": []})
        st.success("✅ 모든 기록이 삭제되었어요!")
        st.rerun()

# 푸터
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    VIK AI Hybrid GraphRAG v2.0 | 
    <a href='http://localhost:8000/docs' target='_blank'>API 문서</a> | 
    <a href='https://github.com' target='_blank'>GitHub</a>
</div>
""", unsafe_allow_html=True)
