# 🚀 VIK AI: Hybrid GraphRAG System

## 📋 개요

VIK AI는 금융 분석을 위한 하이브리드 GraphRAG 시스템이에요!

**핵심 특징**:
- **인덱싱(공부)**: OpenAI API (`gpt-4o-mini`) 사용 → 정확한 금융 수치 추출
- **질문(대화)**: API 또는 LOCAL 모드 선택 가능 → 유연한 사용

## 🏗️ 시스템 구조

```
┌─────────────────────────────────────────────────────────┐
│                    사용자 (브라우저/API)                  │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI 서버 (app.py)                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │  HybridGraphRAGEngine (engine.py)                │  │
│  │                                                   │  │
│  │  인덱싱용 GraphRAG                                │  │
│  │  → OpenAI API (gpt-4o-mini)                     │  │
│  │                                                   │  │
│  │  질문용 GraphRAG (선택 가능)                     │  │
│  │  → OpenAI API 또는 Ollama (llama3.2:3b)        │  │
│  └──────────────────────────────────────────────────┘  │
└───────────────────────┬───────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐              ┌───────────────┐
│  OpenAI API   │              │  Ollama 서버   │
│  (인덱싱)     │              │  (질문 선택)   │
└───────────────┘              └───────────────┘
```

## 📁 파일 구조

```
src/
├── config.py          # 설정 관리 (API 키, 모델 설정)
├── engine.py          # 하이브리드 GraphRAG 엔진
├── app.py             # FastAPI 서버
├── parser.py           # PDF 텍스트 추출
└── streamlit_app.py    # 웹 UI (선택사항)
```

## 🔧 설치 및 설정

### 1. 환경변수 설정

`.env` 파일을 만들고 다음 내용을 추가해요:

```bash
# 실행 모드 (API 또는 LOCAL)
RUN_MODE=API

# OpenAI API 키
OPENAI_API_KEY=sk-your-api-key-here
```

또는 `.env.example`을 복사해서 사용해요:

```bash
cp .env.example .env
# .env 파일을 열어서 OPENAI_API_KEY를 설정해요!
```

### 2. 필요한 패키지 설치

```bash
# 가상환경 활성화
source venv/bin/activate

# 필요한 패키지 설치
pip install openai python-dotenv
```

### 3. Ollama 설정 (LOCAL 모드 사용 시)

```bash
# Ollama 서버 실행
ollama serve

# 필요한 모델 다운로드
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

## 🚀 실행 방법

### 1. FastAPI 서버 실행

```bash
cd /Users/gyuteoi/Desktop/graphRAG
source venv/bin/activate
python3 src/app.py
```

서버 주소: `http://localhost:8000`

### 2. API 사용 예시

#### 인덱싱 (텍스트 추가)

```bash
curl -X POST "http://localhost:8000/insert" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "NVIDIA reported record revenue of $57.0 billion in Q3 2026..."
  }'
```

**응답**:
```json
{
  "message": "텍스트가 성공적으로 인덱싱되었어요! (OpenAI API 사용)",
  "status": "success",
  "mode": "openai_api"
}
```

#### 질문하기 (API 모드)

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is NVIDIA's revenue?",
    "mode": "api"
  }'
```

#### 질문하기 (LOCAL 모드)

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is NVIDIA's revenue?",
    "mode": "local"
  }'
```

**응답**:
```json
{
  "question": "What is NVIDIA's revenue?",
  "answer": "NVIDIA's revenue is $57.0 billion in Q3 2026...",
  "mode": "local",
  "status": "success"
}
```

#### 그래프 현황 확인

```bash
curl "http://localhost:8000/graph_stats"
```

**응답**:
```json
{
  "nodes": 38,
  "edges": 11,
  "status": "success"
}
```

## 📊 API 엔드포인트

### `POST /insert`
텍스트를 인덱싱해요. **항상 OpenAI API를 사용**해요!

**요청 본문**:
```json
{
  "text": "인덱싱할 텍스트"
}
```

### `POST /query`
질문에 답변해요. `mode` 파라미터로 모드를 선택할 수 있어요!

**요청 본문**:
```json
{
  "question": "질문 내용",
  "mode": "api"  // 또는 "local" (기본값: "local")
}
```

### `GET /graph_stats`
그래프 통계를 확인해요!

**응답**:
```json
{
  "nodes": 38,
  "edges": 11,
  "status": "success"
}
```

### `GET /health`
서버 상태를 확인해요!

## 💡 금융 특화 기능

### 우선 추출되는 금융 엔티티

시스템은 다음 금융 지표를 우선적으로 추출해요:

- **REVENUE** (매출)
- **OPERATING_INCOME** (영업이익)
- **NET_INCOME** (순이익)
- **GROWTH_RATE** (성장률)
- **MARGIN** (마진)
- **ASSET** (자산)
- **LIABILITY** (부채)
- **EQUITY** (자본)
- **CASH_FLOW** (현금흐름)
- **EPS** (주당순이익)
- **PE_RATIO** (주가수익비율)
- **MARKET_CAP** (시가총액)

### 금융 특화 프롬프트

`engine.py`의 `get_financial_entity_prompt()` 함수에서 금융 엔티티 추출 프롬프트를 관리해요!

## ⚙️ 설정 옵션

### `config.py` 설정

```python
# 실행 모드
RUN_MODE = "API"  # 또는 "LOCAL"

# OpenAI 모델 설정
API_MODELS = {
    "llm": "gpt-4o-mini",
    "embedding": "text-embedding-3-small",
    "embedding_dim": 1536,
}

# Ollama 모델 설정
LOCAL_MODELS = {
    "llm": "llama3.2:3b",
    "embedding": "nomic-embed-text",
    "embedding_dim": 768,
}
```

## 🔄 파이프라인 흐름

### 인덱싱 파이프라인

```
PDF → parser.py → 텍스트
  → POST /insert
  → HybridGraphRAGEngine.ainsert()
  → OpenAI API (gpt-4o-mini)
  → 엔티티 추출 (금융 특화 프롬프트)
  → 그래프 생성
  → 파일 저장
```

### 질문-답변 파이프라인

```
질문 → POST /query?mode=api 또는 local
  → HybridGraphRAGEngine.aquery()
  → OpenAI API 또는 Ollama
  → 그래프 검색
  → 맥락 조립
  → 답변 생성
```

## 🎯 사용 시나리오

### 시나리오 1: 정확한 인덱싱 + 빠른 질문

1. **인덱싱**: OpenAI API 사용 (정확한 금융 수치 추출)
2. **질문**: LOCAL 모드 사용 (빠르고 비용 없음)

```bash
# 인덱싱
curl -X POST "http://localhost:8000/insert" -d '{"text": "..."}'

# 질문 (LOCAL 모드)
curl -X POST "http://localhost:8000/query" \
  -d '{"question": "...", "mode": "local"}'
```

### 시나리오 2: 모든 작업을 OpenAI API로

```bash
# 인덱싱
curl -X POST "http://localhost:8000/insert" -d '{"text": "..."}'

# 질문 (API 모드)
curl -X POST "http://localhost:8000/query" \
  -d '{"question": "...", "mode": "api"}'
```

## 📝 주의사항

1. **인덱싱은 항상 OpenAI API 사용**: 정확한 금융 수치 추출을 위해!
2. **질문은 선택 가능**: `mode` 파라미터로 선택!
3. **Ollama 서버 실행 필요**: LOCAL 모드 사용 시 `ollama serve` 실행!

## 🐛 문제 해결

### OpenAI API 키 에러

```
❌ API 모드를 사용하려면 OPENAI_API_KEY 환경변수를 설정해주세요!
```

**해결**: `.env` 파일에 `OPENAI_API_KEY` 설정!

### Ollama 연결 에러

```
❌ Ollama 서버에 연결할 수 없어요!
```

**해결**: `ollama serve` 실행!

## 📚 참고 문서

- `ARCHITECTURE.md`: 전체 아키텍처 설명
- `PIPELINE_DIAGRAM.md`: 파이프라인 다이어그램
- `SUMMARY.md`: 프로젝트 요약

