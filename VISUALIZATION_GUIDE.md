# 🎨 그래프 시각화 가이드

## 📋 사용 방법

### 방법 1: Python 스크립트로 실행

```bash
cd /Users/gyuteoi/Desktop/graphRAG
source venv/bin/activate
python3 src/visualize.py
```

**출력 파일**: `graph_ui.html`

### 방법 2: API 엔드포인트 사용

```bash
# 서버 실행 중일 때
curl http://localhost:8000/visualize -o graph_visualization.html

# 또는 브라우저에서
# http://localhost:8000/visualize
```

### 방법 3: 다른 작업 디렉토리 지정

```bash
python3 src/visualize.py graph_storage_api
```

## 🎯 기능

### 시각화 특징

1. **인터랙티브 그래프**
   - 노드를 드래그해서 이동 가능
   - 노드를 클릭하면 연결된 노드 하이라이트
   - 마우스 휠로 확대/축소

2. **색상 구분**
   - **초록색**: ORGANIZATION (회사)
   - **빨간색**: PERSON (사람)
   - **청록색**: GEO (지역)
   - **파란색**: TECHNOLOGY (기술)
   - **노란색**: REVENUE (매출)
   - **주황색**: FINANCIAL (금융)

3. **물리 엔진**
   - 노드들이 자연스럽게 배치됨
   - 연결된 노드들이 가까이 위치

## 📊 현재 그래프 상태

- **노드 수**: 213개
- **엣지 수**: 32개
- **주요 엔티티**: NVIDIA, REVENUE, $57.0 BILLION, Q3 2026 등

## 🔧 커스터마이징

### 색상 변경

`src/visualize.py` 파일에서 `node_colors` 딕셔너리를 수정해요:

```python
node_colors = {
    "ORGANIZATION": "#76b900",  # 여기서 색상 변경
    "PERSON": "#ff6b6b",
    # ...
}
```

### 노드 크기 변경

```python
node["size"] = 20  # 이 값을 변경
```

### 배경색 변경

```python
net = Network(
    bgcolor="#222222",  # 여기서 배경색 변경
    # ...
)
```

## 💡 팁

1. **큰 그래프**: 노드가 많으면 시각화가 느릴 수 있어요
2. **브라우저**: Chrome이나 Firefox에서 가장 잘 작동해요
3. **저장**: HTML 파일을 저장해서 나중에 볼 수 있어요

## 🐛 문제 해결

### 에러: "그래프 파일을 찾을 수 없어요"

**해결**: 먼저 텍스트를 인덱싱해서 그래프를 만들어주세요!

```bash
# API로 인덱싱
curl -X POST http://localhost:8000/insert \
  -H "Content-Type: application/json" \
  -d '{"text": "NVIDIA reported revenue..."}'
```

### 에러: "pyvis 패키지가 설치되지 않았어요"

**해결**:
```bash
pip install pyvis
```

## 📁 생성된 파일

- `graph_ui.html`: 시각화된 그래프 HTML 파일
- 브라우저에서 열어서 인터랙티브하게 탐색할 수 있어요!


