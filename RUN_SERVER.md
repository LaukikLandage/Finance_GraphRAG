# 🚀 서버 실행 가이드

## ⚠️ 중요: 가상환경 활성화 필수!

서버를 실행하기 전에 **반드시 가상환경을 활성화**해야 해요!

## 📋 실행 방법

### 1단계: 가상환경 활성화

```bash
cd /Users/gyuteoi/Desktop/graphRAG
source venv/bin/activate
```

**확인 방법**:
```bash
which python3
# 출력: /Users/gyuteoi/Desktop/graphRAG/venv/bin/python3
```

### 2단계: 서버 실행

```bash
python3 src/app.py
```

**정상 실행 시 출력**:
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
🚀 HybridGraphRAGEngine 초기화 중...
✅ HybridGraphRAGEngine 준비 완료!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 🔍 문제 해결

### 에러: "ModuleNotFoundError: No module named 'fastapi'"

**원인**: 가상환경이 활성화되지 않았어요!

**해결**:
```bash
# 1. 가상환경 활성화 (필수!)
source venv/bin/activate

# 2. 확인
which python3
# 출력이 /Users/gyuteoi/Desktop/graphRAG/venv/bin/python3 이어야 해요!

# 3. 서버 실행
python3 src/app.py
```

### 에러: "address already in use"

**원인**: 포트 8000이 이미 사용 중이에요!

**해결**:
```bash
# 기존 서버 종료
lsof -ti:8000 | xargs kill -9

# 또는 다른 포트 사용
# app.py 마지막 줄 수정: port=8001
```

## ✅ 빠른 체크리스트

실행 전 확인:
- [ ] `cd /Users/gyuteoi/Desktop/graphRAG` 실행했나요?
- [ ] `source venv/bin/activate` 실행했나요?
- [ ] `which python3`가 venv 경로를 가리키나요?
- [ ] `.env` 파일에 `OPENAI_API_KEY` 설정했나요? (API 모드 사용 시)

## 🎯 정상 실행 확인

서버가 정상 실행되면:

1. **터미널 출력 확인**:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

2. **브라우저에서 확인**:
   - http://localhost:8000 접속
   - http://localhost:8000/docs 접속 (Swagger UI)

3. **curl로 확인**:
   ```bash
   curl http://localhost:8000/health
   ```

## 💡 팁

### 백그라운드 실행

```bash
# 백그라운드로 실행
python3 src/app.py > server.log 2>&1 &

# 로그 확인
tail -f server.log

# 종료
pkill -f "python3 src/app.py"
```

### 자동 재시작 (개발용)

```bash
# uvicorn의 --reload 옵션 사용
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```


