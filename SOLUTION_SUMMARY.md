# GraphRAG 답변 생성 문제 해결 요약

## 문제 상황
- GraphRAG가 그래프 데이터를 로드하지만 답변을 생성하지 못함
- 모든 질문에 "Sorry, I'm not able to provide an answer to that question." 응답

## 원인 분석

### 1. Community Reports 부재
- `kv_store_community_reports.json` 파일이 비어있음 (0개 항목)
- NanoGraphRAG 로그: `Each level has communities: {}`

### 2. Graph Cluster Algorithm 문제
- `graspologic` 패키지가 설치되지 않아 더미 모듈 사용
- `graph_cluster_algorithm='leiden'` 설정이 제대로 작동하지 않음
- Community detection이 실행되지 않음

### 3. Query Mode 문제
- `mode='global'`은 community reports가 필수
- Community reports가 없으면 답변 생성 불가

## 해결 방법

### QueryParam mode 변경
```python
# 기존 (작동 안 함)
query_param = QueryParam(
    mode='global',  # community reports 필요!
    top_k=20,
    level=2
)

# 수정 (작동함!)
query_param = QueryParam(
    mode='local',   # 엔티티 기반 검색, community reports 불필요!
    top_k=20,
    level=2
)
```

## 테스트 결과

### 성공 사례
```json
{
  "question": "What is NVIDIA revenue?",
  "answer": "NVIDIA reported $22.1 billion for Q4 2024 and record $57.0 billion for Q3 2026...",
  "mode": "api",
  "status": "success"
}
```

### 답변 내용
- Q4 2024 (ended January 28, 2024): $22.1 billion
- Q3 2026: $57.0 billion (record revenue)
- AI chip business (H100, H200 series) 성장
- Groq 기술 라이선스: $20 billion

## Query Mode 비교

### mode='local' (현재 사용)
- **장점**: Community reports 불필요, 빠른 응답
- **방식**: 엔티티 기반 검색 → 관련 텍스트 청크 검색 → LLM 답변 생성
- **사용 케이스**: 특정 엔티티에 대한 질문

### mode='global' (사용 불가)
- **장점**: 전체 그래프 구조 활용, 복잡한 질문 처리
- **방식**: Community reports 기반 답변 생성
- **필요 조건**: graspologic 패키지, community detection
- **사용 케이스**: 전체적인 트렌드, 복잡한 관계 질문

### mode='naive' (비활성화)
- **장점**: 가장 간단한 RAG
- **방식**: 벡터 유사도 검색 → LLM 답변
- **필요 조건**: `enable_naive_rag=True`

## 적용된 변경사항

### src/engine.py
```python
# Line 303-307
query_param = QueryParam(
    mode='local',  # local 모드 사용!
    top_k=20,
    level=2
)
```

## 향후 개선 방안

### 1. graspologic 설치 (선택사항)
```bash
pip install graspologic
```
- Community detection 활성화
- `mode='global'` 사용 가능

### 2. Community Reports 수동 생성
- 그래프 클러스터링 실행
- Community 요약 리포트 생성

### 3. enable_naive_rag 활성화
```python
GraphRAG(
    working_dir=working_dir,
    enable_naive_rag=True,  # naive 모드 활성화
    ...
)
```

## 결론
- **해결**: `mode='local'`로 변경하여 답변 생성 성공
- **장점**: Community reports 없이도 작동
- **제한**: Global 수준의 복잡한 질문은 처리 어려움
- **권장**: 현재 설정으로 충분히 사용 가능

