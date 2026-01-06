#!/usr/bin/env python3
# test_reindex.py는 "community reports를 생성하면서 재인덱싱하는" 테스트 스크립트예요!

import asyncio
import sys
import os

# src 폴더를 경로에 추가해요!
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from engine import HybridGraphRAGEngine

async def reindex_with_community_reports():
    """
    community reports를 생성하면서 재인덱싱하는 함수예요!
    """
    print("=" * 60)
    print("🔄 Community Reports 생성을 위한 재인덱싱 시작")
    print("=" * 60)
    
    # 1. 엔진 초기화
    print("\n📚 HybridGraphRAGEngine 초기화 중...")
    engine = HybridGraphRAGEngine(working_dir="./graph_storage_hybrid")
    
    # 2. 샘플 텍스트 준비
    sample_texts = [
        """
        NVIDIA Corporation reported record revenue of $57.0 billion for Q3 2026, 
        representing a significant increase in their financial performance. 
        The company's AI chip business, particularly the H100 and H200 series, 
        drove this exceptional growth.
        """,
        """
        NVIDIA's revenue for the fourth quarter ended January 28, 2024 was $22.1 billion.
        The company continues to dominate the AI accelerator market with its advanced GPU technology.
        """,
        """
        In a major acquisition move, Nvidia agreed to license Groq's technology for $20 billion.
        Jonathan Ross, CEO of Groq, and Sunny Madra, president of Groq, will join Nvidia
        to help advance and scale the licensed technology.
        """
    ]
    
    # 3. 각 텍스트를 인덱싱해요!
    for i, text in enumerate(sample_texts, 1):
        print(f"\n📝 텍스트 {i}/{len(sample_texts)} 인덱싱 중...")
        try:
            await engine.ainsert(text)
            print(f"✅ 텍스트 {i} 인덱싱 완료!")
        except Exception as e:
            print(f"❌ 텍스트 {i} 인덱싱 실패: {e}")
            import traceback
            traceback.print_exc()
    
    # 4. 그래프 통계 확인
    print("\n" + "=" * 60)
    print("📊 그래프 통계")
    print("=" * 60)
    stats = engine.get_graph_stats()
    print(f"노드 수: {stats.get('nodes', 0)}")
    print(f"엣지 수: {stats.get('edges', 0)}")
    
    # 5. community reports 파일 확인
    print("\n" + "=" * 60)
    print("📁 Community Reports 파일 확인")
    print("=" * 60)
    
    import json
    community_reports_path = os.path.join(engine.working_dir, "kv_store_community_reports.json")
    if os.path.exists(community_reports_path):
        with open(community_reports_path, 'r') as f:
            data = json.load(f)
            print(f"✅ community_reports 항목 수: {len(data)}")
            if len(data) > 0:
                print("첫 번째 리포트 키:", list(data.keys())[0])
    else:
        print(f"⚠️  community_reports 파일이 아직 없어요: {community_reports_path}")
        # 다른 경로도 확인해요!
        alt_paths = [
            "community_reports.json",
            "kv_store_community_reports.json"
        ]
        for alt_path in alt_paths:
            full_path = os.path.join(engine.working_dir, alt_path)
            if os.path.exists(full_path):
                print(f"✅ 대체 경로 발견: {alt_path}")
                break
    
    # 6. 질문 테스트
    print("\n" + "=" * 60)
    print("🔍 질문 테스트")
    print("=" * 60)
    
    test_questions = [
        "What is NVIDIA revenue?",
        "Tell me about NVIDIA's financial performance",
        "What is the Groq acquisition about?"
    ]
    
    for question in test_questions:
        print(f"\n질문: {question}")
        try:
            response = await engine.aquery(question, mode="api")
            print(f"답변: {response[:300]}...")
        except Exception as e:
            print(f"에러: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 재인덱싱 완료!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(reindex_with_community_reports())

