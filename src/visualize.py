# visualize.py는 "그래프를 시각화하는" 파일이에요!
# 마치 "그래프를 예쁘게 그려주는 도구" 같은 거예요!

# networkx는 그래프를 다루는 도구예요!
# 마치 "그래프를 읽고 쓸 수 있는 도구" 같은 거예요!
import networkx as nx
# pyvis는 그래프를 인터랙티브하게 시각화하는 도구예요!
# 마치 "그래프를 웹페이지로 보여주는 도구" 같은 거예요!
from pyvis.network import Network
# os는 파일 경로를 다루는 도구예요!
import os
# sys는 시스템 관련 작업을 하는 도구예요!
import sys

def visualize_graph(working_dir="./graph_storage_hybrid", output_file="graph_ui.html"):
    """
    GraphRAG 그래프를 시각화하는 함수예요!
    
    Args:
        working_dir: 그래프 데이터가 있는 폴더 경로
        output_file: 생성할 HTML 파일 이름
        
    Returns:
        생성된 HTML 파일 경로
    """
    try:
        # 1. 그래프 파일 경로
        graphml_path = os.path.join(working_dir, "graph_chunk_entity_relation.graphml")
        
        # 파일이 있는지 확인해요!
        if not os.path.exists(graphml_path):
            print(f"❌ 그래프 파일을 찾을 수 없어요: {graphml_path}")
            print("💡 먼저 텍스트를 인덱싱해서 그래프를 만들어주세요!")
            return None
        
        print(f"📖 그래프 파일 읽는 중: {graphml_path}")
        
        # 2. GraphML 파일을 읽어서 NetworkX 그래프로 변환해요!
        # nx.read_graphml()은 GraphML 파일을 읽어서 그래프로 만드는 거예요!
        G = nx.read_graphml(graphml_path)
        
        print(f"✅ 그래프 로드 완료!")
        print(f"   - 노드 수: {G.number_of_nodes()}")
        print(f"   - 엣지 수: {G.number_of_edges()}")
        
        # 3. Pyvis Network 객체 생성
        # Network()는 "시각화할 그래프를 담을 상자"예요!
        # notebook=False는 "Jupyter Notebook이 아닌 일반 HTML 파일로 만들자"는 뜻이에요!
        # height="750px"는 "높이를 750픽셀로 설정"이라는 뜻이에요!
        # width="100%"는 "너비를 100%로 설정"이라는 뜻이에요!
        # bgcolor="#222222"는 "배경색을 어두운 회색으로 설정"이라는 뜻이에요!
        # font_color="white"는 "글자색을 흰색으로 설정"이라는 뜻이에요!
        net = Network(
            notebook=False,
            height="750px",
            width="100%",
            bgcolor="#222222",
            font_color="white"
        )
        
        # 4. NetworkX 그래프를 Pyvis로 변환해요!
        # net.from_nx()는 NetworkX 그래프를 Pyvis 형식으로 변환하는 거예요!
        net.from_nx(G)
        
        # 5. 노드 스타일 설정 (더 예쁘게 만들기!)
        # 노드 타입에 따라 색상을 다르게 설정해요!
        node_colors = {
            "ORGANIZATION": "#76b900",  # NVIDIA 같은 회사는 초록색
            "PERSON": "#ff6b6b",        # 사람은 빨간색
            "GEO": "#4ecdc4",           # 지역은 청록색
            "TECHNOLOGY": "#0077ff",    # 기술은 파란색
            "REVENUE": "#ffcc00",       # 매출은 노란색
            "FINANCIAL": "#ff9500",     # 금융 관련은 주황색
        }
        
        # 각 노드에 색상과 크기 설정해요!
        for node in net.nodes:
            node_id = node.get("id", "")
            node_label = node.get("label", node_id)
            
            # 노드 ID에서 엔티티 타입 추출 시도
            node_color = "#95a5a6"  # 기본 색상 (회색)
            for entity_type, color in node_colors.items():
                if entity_type in str(node_id).upper():
                    node_color = color
                    break
            
            # 노드 스타일 설정
            node["color"] = node_color
            node["size"] = 20  # 노드 크기
            node["font"] = {"size": 12, "color": "white"}
            
            # 노드 ID에서 따옴표 제거 (보기 좋게!)
            if node_id.startswith('"') and node_id.endswith('"'):
                node["label"] = node_id[1:-1]  # 앞뒤 따옴표 제거
            else:
                node["label"] = node_id
        
        # 6. 엣지 스타일 설정
        for edge in net.edges:
            edge["color"] = {"color": "#95a5a6", "highlight": "#3498db"}
            edge["width"] = 2
        
        # 7. 물리 엔진 설정 (그래프가 더 자연스럽게 배치되도록!)
        # physics는 "물리 엔진"이에요. 노드들이 서로 밀고 당기면서 자연스럽게 배치돼요!
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -2000,
              "centralGravity": 0.1,
              "springLength": 200,
              "springConstant": 0.04
            }
          }
        }
        """)
        
        # 8. HTML 파일로 저장해요!
        # net.write_html()는 HTML 파일을 생성하는 거예요!
        output_path = os.path.abspath(output_file)
        # notebook=False로 설정해서 일반 HTML 파일로 생성해요!
        net.write_html(output_path, notebook=False)
        
        print(f"🎨 그래프 시각화 완료!")
        print(f"📄 파일 위치: {output_path}")
        print(f"🌐 브라우저에서 열어보세요!")
        
        return output_path
        
    except FileNotFoundError as e:
        print(f"❌ 파일을 찾을 수 없어요: {e}")
        return None
    except Exception as e:
        print(f"❌ 에러 발생: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None

# if __name__ == "__main__": 이건 "이 파일을 직접 실행했을 때만"이라는 뜻이에요!
if __name__ == "__main__":
    # sys.argv는 "명령줄에서 입력한 인자들"이에요!
    # 예: python3 visualize.py graph_storage_hybrid
    #     sys.argv[0] = "visualize.py"
    #     sys.argv[1] = "graph_storage_hybrid" (선택사항)
    
    # working_dir은 명령줄 인자로 받거나 기본값 사용해요!
    working_dir = sys.argv[1] if len(sys.argv) > 1 else "./graph_storage_hybrid"
    
    print("=" * 60)
    print("🎨 GraphRAG 그래프 시각화")
    print("=" * 60)
    print(f"📁 작업 디렉토리: {working_dir}")
    print()
    
    # visualize_graph 함수를 호출해요!
    result = visualize_graph(working_dir=working_dir)
    
    if result:
        print()
        print("=" * 60)
        print("✅ 시각화 성공!")
        print("=" * 60)
    else:
        print()
        print("=" * 60)
        print("❌ 시각화 실패!")
        print("=" * 60)