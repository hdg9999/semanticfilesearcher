import os
import sys
import numpy as np

# core 모듈 경로 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from core.embedding.qwen_adapter import QwenEmbeddingAdapter
from core.database.vector_db import VectorDBManager
from core.database.sqlite_manager import DatabaseManager

def main():
    print("Loading embedding adapter...")
    adapter = QwenEmbeddingAdapter()
    
    # 임시 테스트용 데이터베이스 초기화
    test_db_dir = os.path.join(os.path.dirname(__file__), "data", "test_db")
    os.makedirs(test_db_dir, exist_ok=True)
    
    print(f"\nInitializing Vector DB with dimension {adapter.dimension}...")
    vector_db_path = os.path.join(test_db_dir, "lancedb")
    # 기존 테스트 DB가 있다면 삭제 로직을 넣거나 덮어쓰기
    vector_db = VectorDBManager(dimension=adapter.dimension, index_path=vector_db_path)
    
    queries = ["강아지", "개", "dog", "puppy", "자동차", "차", "car", "사람", "people", "노란색 개 한머리가 도로 위에 있음"]
    
    image_dir = r"C:\Users\hdg99\Documents\사진들"
    image_files = [
        "진도개1.jpg", "진도개2.jpg", 
        "자동차2.jpg", "XM3 자동차.jpg", 
        "사람들2.jpg", "사람1.jpg",
        "도2시.png", "진도개3.jpg"
    ]
    
    image_paths = [os.path.join(image_dir, f) for f in image_files]
    
    print("\nEncoding images and adding to LanceDB...")
    
    vectors_to_add = []
    vector_ids = []
    
    # 파일 이름과 벡터 ID 매핑을 위한 딕셔너리
    id_to_filename = {}
    
    for i, (path, filename) in enumerate(zip(image_paths, image_files)):
        print(f"  Encoding {filename}...")
        try:
            emb = adapter.encode_image(path)
            # encode_image는 (1, dim) 형태 배열 반환을 가정하거나 다중 반환일 수 있으므로 0번째 요소 사용
            vectors_to_add.append(emb[0])
            vector_ids.append(i + 1) # ID는 1부터 시작
            id_to_filename[i + 1] = filename
        except Exception as e:
            print(f"  Failed: {e}")
            
    if vectors_to_add:
        print("\nAdding vectors to LanceDB...")
        vectors_np = np.array(vectors_to_add)
        vector_db.add_vectors(vectors_np, vector_ids)
        print("Vectors added successfully.")
    else:
        print("No vectors to add. Exiting.")
        return

    print("\n--- LanceDB Vector Search Results ---")
    print("LanceDB uses cosine distance, but VectorDBManager converts it to cosine similarity (1 - distance)")
    
    for query in queries:
        print(f"\n--- Query: '{query}' ---")
        try:
            q_emb = adapter.encode_text(query)
            
            # vector_db search는 리스트 형태의 딕셔너리를 반환함 [{"vector_id": 1, "distance": 0.8}, ...]
            # q_emb는 현재 (dim,) 이 아닌 (1, dim) 이여야 하지만, vector_db.search 내부 처리를 살펴보고 맞춰 줌
            if len(q_emb.shape) == 1:
                 q_emb = np.expand_dims(q_emb, axis=0) # (1, dim) 형태로 맞춤
                 
            results = vector_db.search(q_emb, top_k=50) # top_k는 충분히 크게
            
            for res in results:
                vid = res['vector_id']
                sim = res['distance'] # VectorDBManager.search 반환값은 similarity로 변환되어 있음
                filename = id_to_filename.get(vid, "Unknown")
                print(f"{sim:.4f} : {filename}")
                
        except Exception as e:
            print(f"  Search failed: {e}")

if __name__ == "__main__":
    main()
