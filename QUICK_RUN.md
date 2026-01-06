# ⚡ 빠른 실행 가이드

## 🚀 서버 실행 (가장 간단한 방법)

```bash
cd /Users/gyuteoi/Desktop/graphRAG
source venv/bin/activate
python3 src/app.py
```

## 📝 단계별 설명

### 1. 프로젝트 폴더로 이동
```bash
cd /Users/gyuteoi/Desktop/graphRAG
```

### 2. 가상환경 활성화 (필수!)
```bash
source venv/bin/activate
```

**확인**: 터미널 앞에 `(venv)`가 보이면 성공!

### 3. 서버 실행
```bash
python3 src/app.py
```

## ✅ 정상 실행 확인

서버가 정상 실행되면:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

브라우저에서 확인:
- http://localhost:8000
- http://localhost:8000/docs

## 🔧 문제 해결

### "ModuleNotFoundError: No module named 'fastapi'"

**해결**: 가상환경을 활성화했는지 확인!
```bash
source venv/bin/activate
which python3  # venv 경로여야 해요!
```

### "address already in use"

**해결**: 기존 서버 종료
```bash
lsof -ti:8000 | xargs kill -9
```

## 💡 편리한 실행 스크립트

`run_server.sh` 파일을 만들었어요:
```bash
./run_server.sh
```


