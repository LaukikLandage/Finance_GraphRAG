#!/bin/bash
# 서버 실행 스크립트

cd /Users/gyuteoi/Desktop/graphRAG
source venv/bin/activate
python3 src/app.py

# 그래프 시각화 
python3 src/visualize.py
open graph_ui.html

# url 추가 방법
echo "http://localhost:8000/visualize" >> ~/.zshrc
source ~/.zshrc

# streamlit 실행
streamlit run src/streamlit_app.py