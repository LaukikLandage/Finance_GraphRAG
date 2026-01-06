# ⚡ 빠른 시작 가이드

## 1️⃣ 환경 설정

### `.env` 파일 만들기

프로젝트 루트에 `.env` 파일을 만들고 다음 내용을 추가해요:

```bash
# 실행 모드 (API 또는 LOCAL)
RUN_MODE=API

# OpenAI API 키 (https://platform.openai.com/api-keys 에서 발급)
OPENAI_API_KEY=sk-your-api-key-here
```

### 필요한 패키지 설치

```bash
# 가상환경 활성화
source venv/bin/activate

# python-dotenv 설치 (.env 파일 읽기용)
pip install python-dotenv openai
```

## 2️⃣ 서버 실행

```bash
cd /Users/gyuteoi/Desktop/graphRAG
source venv/bin/activate
python3 src/app.py
```

서버가 실행되면: `http://localhost:8000`

## 3️⃣ 사용 예시

### 인덱싱 (텍스트 추가)

```bash
curl -X POST "http://localhost:8000/insert" \
  -H "Content-Type: application/json" \
  -d '{"text": "NVIDIA reported revenue of $57.0 billion..."}'
```

### 질문하기 (LOCAL 모드 - 기본값)

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is NVIDIA revenue?", "mode": "local"}'
```

### 질문하기 (API 모드)

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is NVIDIA revenue?", "mode": "api"}'
```

## 4️⃣ API 문서 보기

브라우저에서 `http://localhost:8000/docs` 접속하면 Swagger UI로 API를 테스트할 수 있어요!

## 💡 핵심 포인트

- **인덱싱**: 항상 OpenAI API 사용 (정확한 금융 수치 추출)
- **질문**: `mode` 파라미터로 "api" 또는 "local" 선택 가능
- **LOCAL 모드 사용 시**: `ollama serve` 실행 필요!

