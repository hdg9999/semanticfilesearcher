import os
# AhnLab/Banking security OpenSSL Applink crash fix
os.environ.pop("SSLKEYLOGFILE", None)
import sys
import shutil
import time
import numpy as np

# core 모듈을 import 하기 위해 시스템 경로에 프로젝트 루트 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.indexer import SemanticIndexer
from core.embedding.qwen_adapter import QwenEmbeddingAdapter
from core.database.vector_db import VectorDBManager
from core.database.sqlite_manager import DatabaseManager

def test_core_features():
    print("=== Testing Core Features ===")
    
    # 1. 테스트용 임시 디렉토리 설정
    test_data_dir = os.path.join(os.path.dirname(__file__), "test_data_dir")
    test_index_dir = os.path.join(os.path.dirname(__file__), "test_index_dir")
    
    os.makedirs(test_data_dir, exist_ok=True)
    os.makedirs(test_index_dir, exist_ok=True)
    
    # 더미 파일 생성
    dummy_txt_path = os.path.join(test_data_dir, "hello.txt")
    with open(dummy_txt_path, "w", encoding="utf-8") as f:
        f.write("안녕하세요, 이것은 테스트 문서입니다. 강아지와 고양이가 있습니다.")
        
    try:
        print("\n1. 임베딩 모델 로드 및 인코딩 테스트...")
        adapter = QwenEmbeddingAdapter()
        text_emb = adapter.encode_text("강아지와 고양이")
        print(f" - Text embedding shape: {text_emb.shape}")
        if len(text_emb.shape) == 1 and text_emb.shape[0] == adapter.dimension:
            pass # OK
        elif len(text_emb.shape) == 2 and text_emb.shape[1] == adapter.dimension:
            text_emb = text_emb[0] # Flatten
        else:
            raise ValueError(f"Invalid text embedding shape: {text_emb.shape}")
            
        print("\n2. 벡터 DB 생성 및 벡터 검색 테스트...")
        vector_db_path = os.path.join(test_index_dir, "lancedb")
        vdb = VectorDBManager(dimension=adapter.dimension, index_path=vector_db_path)
        
        # 임의의 백터 및 ID 추가
        dummy_vectors = np.array([text_emb])
        vdb.add_vectors(dummy_vectors, [1])
        
        # 검색 테스트
        search_results = vdb.search(np.array([text_emb]), top_k=1)
        print(f" - Vector Search results: {search_results}")
        if not search_results or search_results[0]['vector_id'] != 1:
            raise ValueError("Vector search failed to retrieve the correct ID.")
            
        print("\n3. RDB 생성 및 태그 로직 테스트...")
        sqlite_path = os.path.join(test_index_dir, "metadata.db")
        rdb = DatabaseManager(sqlite_path)
        
        # 메타데이터 및 태그 삽입
        rdb.upsert_file(dummy_txt_path, time.time()) # path, mtime
        file_m = rdb.get_file_metadata(dummy_txt_path)
        if not file_m:
            raise ValueError("Failed to retrieve file metadata.")
            
        rdb.update_file_tags(dummy_txt_path, ["테스트", "문서"])
        
        tag_search_results = rdb.search_by_tags(["테스트"])
        print(f" - Tag Search results: {tag_search_results}")
        if not tag_search_results or dummy_txt_path not in tag_search_results:
            raise ValueError("Tag search failed to retrieve the file.")
            
        print("\n4. 통합 검색 연동 테스트 (SemanticIndexer)...")
        # indexer 초기화 (위의 sqlite 경로가 다를 수 있지만 ConfigManager가 기본값 사용)
        # 테스트를 위해 간단히 SemanticIndexer 인스턴스화 속도 및 예외 여부만 체크
        indexer = SemanticIndexer(data_dir=test_index_dir)
        print(" - SemanticIndexer initialized successfully.")
        
        # 검색 기능 단순 호출
        indexer.search("강아지", mode="통합 검색")
        print(" - Search call completed without exception.")

        print("\n=== All tests passed successfully! ===")
        
    except Exception as e:
        print(f"\n[ERROR] Core feature test failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # 정리
        print("Cleaning up test directories...")
        time.sleep(1) # 파일 핸들 해제 대기
        try:
            if os.path.exists(test_data_dir):
                shutil.rmtree(test_data_dir, ignore_errors=True)
            if os.path.exists(test_index_dir):
                shutil.rmtree(test_index_dir, ignore_errors=True)
        except Exception as cleanup_err:
            print(f"Cleanup warning: {cleanup_err}")

if __name__ == "__main__":
    test_core_features()
