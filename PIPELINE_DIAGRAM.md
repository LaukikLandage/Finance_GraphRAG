# 🔄 Financial GraphRAG 파이프라인 상세 다이어그램

## 📊 현재 그래프 상태

- **노드 수**: 38개 (엔티티들)
- **엣지 수**: 11개 (관계들)
- **예시 노드**: NVIDIA, COLETTE KRESS, USA, GERMANY, H100 등

---

## 🔄 전체 파이프라인 흐름도

```
┌─────────────────────────────────────────────────────────────────┐
│                        사용자 액션                               │
│  "PDF 업로드" 또는 "질문하기"                                    │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐              ┌───────────────┐
│  인덱싱 모드  │              │  질문 모드    │
│  (Insert)     │              │  (Query)      │
└───────┬───────┘              └───────┬───────┘
        │                               │
        │                               │
        ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                           │
│  ┌──────────────┐              ┌──────────────┐                │
│  │ PDF 업로드   │              │  채팅 입력   │                │
│  │ 버튼 클릭    │              │  엔터 치기   │                │
│  └──────┬───────┘              └──────┬───────┘                │
│         │                              │                        │
│         │ HTTP POST /insert           │ HTTP POST /query       │
│         ▼                              ▼                        │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend Layer                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  graph_rag = GraphRAG(                                   │  │
│  │    working_dir="./my_graph_data",                        │  │
│  │    best_model_func=ollama_model_if,                      │  │
│  │    embedding_func=ollama_embedding_if                    │  │
│  │  )                                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────┐              ┌──────────────┐               │
│  │ /insert      │              │ /query       │               │
│  │ endpoint     │              │ endpoint     │               │
│  └──────┬───────┘              └──────┬───────┘               │
│         │                              │                       │
│         │ graph_rag.ainsert()          │ graph_rag.aquery()    │
│         ▼                              ▼                       │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│              NanoGraphRAG 엔진 (내부 처리)                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 인덱싱 파이프라인 상세 (Insert)

```
[1단계] PDF → 텍스트
┌─────────────────────────────────────────┐
│ parser.extract_text_from_pdf()         │
│                                         │
│  PDF 파일                               │
│    ↓                                    │
│  PyMuPDF로 읽기                         │
│    ↓                                    │
│  각 페이지 텍스트 추출                  │
│    ↓                                    │
│  하나의 긴 문자열                       │
│  "NVIDIA reported record revenue..."   │
└─────────────────────────────────────────┘
                    ↓
[2단계] 텍스트 → Chunks (조각)
┌─────────────────────────────────────────┐
│ GraphRAG.ainsert(text)                 │
│                                         │
│  긴 텍스트                              │
│    ↓                                    │
│  Chunking (1200 토큰 단위로 자르기)     │
│    ↓                                    │
│  [chunk1, chunk2, chunk3, ...]          │
│  ┌──────────┐  ┌──────────┐            │
│  │ chunk-1  │  │ chunk-2  │  ...       │
│  │ "NVIDIA  │  │ "The H100│            │
│  │  reported│  │  GPU is  │            │
│  │  record  │  │  designed│            │
│  │  revenue"│  │  for..." │            │
│  └──────────┘  └──────────┘            │
│                                         │
│  저장: kv_store_text_chunks.json       │
└─────────────────────────────────────────┘
                    ↓
[3단계] 각 Chunk → 엔티티 추출
┌─────────────────────────────────────────┐
│ Entity Extraction (각 chunk마다)       │
│                                         │
│  chunk-1                                │
│    ↓                                    │
│  Ollama(llama3.2:3b) 호출              │
│  "이 텍스트에서 중요한 단어 찾아줘"      │
│    ↓                                    │
│  엔티티 리스트:                         │
│  - NVIDIA (ORGANIZATION)               │
│  - $57.0 billion (MONEY)                │
│  - Q3 2026 (DATE)                       │
│                                         │
│  chunk-2 → 같은 과정 반복...            │
│                                         │
│  저장: kv_store_llm_response_cache.json│
└─────────────────────────────────────────┘
                    ↓
[4단계] 엔티티 → 벡터화
┌─────────────────────────────────────────┐
│ Embedding (각 엔티티마다)               │
│                                         │
│  "NVIDIA"                               │
│    ↓                                    │
│  Ollama(nomic-embed-text) 호출         │
│    ↓                                    │
│  768차원 벡터:                          │
│  [0.123, -0.456, 0.789, ...]           │
│                                         │
│  모든 엔티티 벡터화                     │
│                                         │
│  저장: vdb_entities.json               │
└─────────────────────────────────────────┘
                    ↓
[5단계] 그래프 구축
┌─────────────────────────────────────────┐
│ Graph Building                          │
│                                         │
│  엔티티들:                              │
│  - NVIDIA                               │
│  - H100                                 │
│  - TSMC                                 │
│    ↓                                    │
│  관계 찾기:                             │
│  - NVIDIA → produces → H100            │
│  - H100 → manufactured_by → TSMC       │
│    ↓                                    │
│  그래프 생성:                           │
│                                         │
│    NVIDIA ──produces──> H100           │
│      │                                  │
│      │                                  │
│    TSMC <──manufactured_by── H100      │
│                                         │
│  저장: graph_chunk_entity_relation.graphml│
└─────────────────────────────────────────┘
                    ↓
[완료] ✅ 그래프 생성 완료!
```

---

## 🔍 질문-답변 파이프라인 상세 (Query)

```
[1단계] 질문 입력
┌─────────────────────────────────────────┐
│ 사용자: "What is NVIDIA's revenue?"    │
└─────────────────────────────────────────┘
                    ↓
[2단계] 질문 벡터화
┌─────────────────────────────────────────┐
│ Query Embedding                         │
│                                         │
│  "What is NVIDIA's revenue?"           │
│    ↓                                    │
│  Ollama(nomic-embed-text) 호출         │
│    ↓                                    │
│  768차원 벡터:                          │
│  [0.234, -0.567, 0.890, ...]           │
└─────────────────────────────────────────┘
                    ↓
[3단계] 유사 엔티티 검색
┌─────────────────────────────────────────┐
│ Entity Retrieval                        │
│                                         │
│  질문 벡터                              │
│    ↓                                    │
│  vdb_entities.json에서                 │
│  코사인 유사도 계산                     │
│    ↓                                    │
│  가장 유사한 엔티티들:                  │
│  1. "NVIDIA" (유사도: 0.95)            │
│  2. "revenue" (유사도: 0.87)            │
│  3. "$57.0 billion" (유사도: 0.82)     │
└─────────────────────────────────────────┘
                    ↓
[4단계] 그래프 탐색
┌─────────────────────────────────────────┐
│ Graph Traversal                         │
│                                         │
│  "NVIDIA" 노드 찾기                     │
│    ↓                                    │
│  graph_chunk_entity_relation.graphml   │
│  에서 연결된 노드들 찾기:               │
│                                         │
│    NVIDIA                               │
│      │                                  │
│      ├─> H100                          │
│      ├─> revenue ($57.0B)              │
│      └─> Q3 2026                       │
│                                         │
│  관련 chunk ID들 수집:                  │
│  - chunk-abc123                         │
│  - chunk-def456                         │
└─────────────────────────────────────────┘
                    ↓
[5단계] 맥락 조립
┌─────────────────────────────────────────┐
│ Context Assembly                        │
│                                         │
│  chunk ID들                             │
│    ↓                                    │
│  kv_store_text_chunks.json에서         │
│  원문 가져오기:                         │
│                                         │
│  "NVIDIA reported record revenue       │
│   of $57.0 billion in Q3 2026..."     │
│                                         │
│  "The H100 GPU contributed to          │
│   the revenue growth..."               │
│                                         │
│  → 하나의 "맥락" 문자열로 합치기        │
└─────────────────────────────────────────┘
                    ↓
[6단계] 답변 생성
┌─────────────────────────────────────────┐
│ LLM Generation                           │
│                                         │
│  맥락 + 질문                            │
│    ↓                                    │
│  Ollama(llama3.2:3b) 호출              │
│  "이 맥락을 보고 질문에 답해줘"          │
│    ↓                                    │
│  최종 답변:                             │
│  "NVIDIA's revenue is $57.0 billion   │
│   in the third quarter of fiscal 2026."│
└─────────────────────────────────────────┘
                    ↓
[완료] ✅ 답변 반환!
```

---

## 💾 데이터 저장 구조 상세

### 파일별 역할

```
graph_storage/
│
├── graph_chunk_entity_relation.graphml
│   └─ 역할: 그래프 구조 (노드 + 엣지)
│   └─ 형식: XML (GraphML)
│   └─ 내용:
│       - 노드: 엔티티들 (NVIDIA, H100, ...)
│       - 엣지: 관계들 (produces, located_in, ...)
│
├── kv_store_text_chunks.json
│   └─ 역할: 원본 텍스트 조각 저장
│   └─ 형식: JSON {chunk_id: "텍스트"}
│   └─ 예시:
│       {
│         "chunk-abc123": "NVIDIA reported...",
│         "chunk-def456": "The H100 GPU..."
│       }
│
├── vdb_entities.json
│   └─ 역할: 엔티티 벡터 데이터베이스
│   └─ 형식: JSON (nano-vectordb)
│   └─ 내용:
│       - 각 엔티티의 768차원 벡터
│       - 벡터 검색 인덱스
│
├── kv_store_llm_response_cache.json
│   └─ 역할: LLM 응답 캐시
│   └─ 형식: JSON {prompt_hash: "응답"}
│   └─ 목적: 같은 질문이 오면 재사용
│
├── kv_store_full_docs.json
│   └─ 역할: 전체 문서 저장
│   └─ 형식: JSON
│
└── kv_store_community_reports.json
    └─ 역할: 커뮤니티 리포트 저장
    └─ 형식: JSON
```

---

## 🔄 데이터 흐름 요약

### 인덱싱 시 데이터 흐름

```
PDF 파일
  → parser.py (텍스트 추출)
  → 긴 문자열
  → GraphRAG.ainsert()
  → Chunking (조각 나누기)
  → 각 chunk → Entity Extraction (Ollama)
  → 엔티티들 → Embedding (Ollama)
  → 벡터들 → vdb_entities.json
  → 관계 찾기 → Graph Building
  → graph_chunk_entity_relation.graphml
```

### 질문 시 데이터 흐름

```
질문 문자열
  → Query Embedding (Ollama)
  → 질문 벡터
  → vdb_entities.json (벡터 검색)
  → 유사 엔티티들
  → graph_chunk_entity_relation.graphml (그래프 탐색)
  → 관련 chunk ID들
  → kv_store_text_chunks.json (원문 가져오기)
  → 맥락 문자열
  → LLM Generation (Ollama)
  → 최종 답변
```

---

## 🎯 핵심 포인트

1. **Chunking**: 긴 텍스트를 작은 조각으로 나눔 (1200 토큰 단위)
2. **Entity Extraction**: 각 chunk에서 중요한 단어(엔티티) 추출
3. **Embedding**: 엔티티를 숫자 벡터로 변환 (검색용)
4. **Graph Building**: 엔티티들 간의 관계를 그래프로 표현
5. **Retrieval**: 질문과 유사한 엔티티를 벡터 검색으로 찾기
6. **Context Assembly**: 관련 텍스트를 모아서 맥락 만들기
7. **Generation**: 맥락을 보고 LLM이 답변 생성

