# 🚀 API 모드 사용 가이드

## 📋 API 모드란?

API 모드는 **OpenAI API를 사용해서 답변을 생성하는 모드**예요!

**장점**:
- ✅ Ollama 서버 불필요
- ✅ 더 정확한 답변
- ✅ 안정적

**단점**:
- ⚠️ OpenAI API 비용 발생

## 🔧 사용 방법

### 방법 1: 명령줄에서 실행

```bash
cd /Users/gyuteoi/Desktop/graphRAG
source venv/bin/activate

# API 모드로 질문하기
python3 src/ask_graphrag.py "질문 내용" api
```

**예시**:
```bash
# 기본 질문
python3 src/ask_graphrag.py "What is NVIDIA revenue?" api

# 한글 질문
python3 src/ask_graphrag.py "엔비디아의 매출은?" api

# 복잡한 질문
python3 src/ask_graphrag.py "What is the relationship between NVIDIA and revenue?" api
```

### 방법 2: Python 코드에서 사용

```python
from ask_graphrag import ask_graph_rag

# API 모드로 질문
result = ask_graph_rag("What is NVIDIA revenue?", mode="api")
print(result)
```

### 방법 3: 직접 API 호출

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is NVIDIA revenue?", "mode": "api"}'
```

## ⚙️ 설정 필요 사항

### 1. OpenAI API 키 설정

`.env` 파일에 API 키를 설정해요:

```bash
OPENAI_API_KEY=sk-your-api-key-here
```

**API 키 발급**:
1. https://platform.openai.com/api-keys 접속
2. "Create new secret key" 클릭
3. 생성된 키를 `.env` 파일에 추가

### 2. FastAPI 서버 실행

```bash
cd /Users/gyuteoi/Desktop/graphRAG
source venv/bin/activate
python3 src/app.py
```

## 📊 사용 예시

### 예시 1: 기본 질문

```bash
python3 src/ask_graphrag.py "What is NVIDIA?" api
```

**출력**:
```
============================================================
🚀 GraphRAG 질문-답변 시작
============================================================
🔍 질문: What is NVIDIA?
🔧 모드: api
⏳ 답변 생성 중...

🤖 AI의 답변 (api 모드):
============================================================
[답변 내용]
============================================================
```

### 예시 2: 한글 질문

```bash
python3 src/ask_graphrag.py "엔비디아의 매출은 얼마야?" api
```

### 예시 3: 복잡한 질문

```bash
python3 src/ask_graphrag.py "What is the relationship between NVIDIA and revenue in Q3 2026?" api
```

## 🔄 LOCAL 모드 vs API 모드

| 항목 | LOCAL 모드 | API 모드 |
|------|-----------|---------|
| **서버 필요** | Ollama 서버 필요 | 불필요 |
| **비용** | 무료 | 유료 (OpenAI API) |
| **속도** | 보통 | 빠름 |
| **정확도** | 보통 | 높음 |
| **안정성** | Ollama 서버 의존 | 안정적 |

## 💡 추천 사용법

### 개발/테스트: API 모드
- Ollama 서버 설정 불필요
- 빠르고 안정적
- 테스트하기 좋아요

### 프로덕션: LOCAL 모드
- 비용 없음
- 하지만 Ollama 서버 필요

## 🐛 문제 해결

### 에러: "OpenAI API 키가 없어요"

**해결**:
```bash
# .env 파일 확인
cat .env

# .env 파일에 추가
echo "OPENAI_API_KEY=sk-your-key" >> .env
```

### 에러: "서버에 연결할 수 없어요"

**해결**:
```bash
# FastAPI 서버 실행 확인
curl http://localhost:8000/health

# 서버 시작
python3 src/app.py
```

### 에러: "할당량 초과"

**해결**:
- OpenAI 계정의 사용량 확인
- 결제 정보 업데이트
- 또는 LOCAL 모드 사용

## 📝 요약

**API 모드 사용법**:
```bash
python3 src/ask_graphrag.py "질문" api
```

**필수 조건**:
1. ✅ `.env` 파일에 `OPENAI_API_KEY` 설정
2. ✅ FastAPI 서버 실행 중 (`python3 src/app.py`)

**장점**: Ollama 서버 없이도 사용 가능!


