import os
import sys
import numpy as np

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database.deprecated.vector_db_faiss import VectorDBManager as FaissManager
from core.database.vector_db import VectorDBManager as LanceDBManager
from core.embedding.qwen_adapter import QwenEmbeddingAdapter
import faiss

def migrate():
    data_dir = "data"
    faiss_path = os.path.join(data_dir, "vector.faiss")
    lancedb_path = os.path.join(data_dir, "lancedb")

    if not os.path.exists(faiss_path):
        print(f"FAISS index not found at {faiss_path}. Nothing to migrate.")
        return

    # OpenSSL 에러 등을 피하기 위해 모델 인스턴스화 없이 차원 지정
    print("Setting dimension to 2048...")
    dimension = 2048

    print(f"Loading FAISS DB from {faiss_path}...")
    faiss_db = FaissManager(dimension, faiss_path)
    ntotal = faiss_db.index.ntotal
    print(f"Total vectors in FAISS: {ntotal}")
    
    if ntotal == 0:
        print("No data in FAISS index to migrate.")
        return

    print("Extracting vectors and IDs from FAISS index...")
    # Get all vectors from base index
    base_index = faiss_db.index.index
    vectors = np.zeros((ntotal, dimension), dtype=np.float32)
    for i in range(ntotal):
        try:
            vectors[i] = base_index.reconstruct(i)
        except Exception as e:
            print(f"Failed to reconstruct vector at index {i}: {e}")
            
    # Get IDs from id_map
    vector_ids = faiss.vector_to_array(faiss_db.index.id_map)

    print(f"Extracted {len(vectors)} vectors and {len(vector_ids)} IDs.")

    print(f"Initializing LanceDB at {lancedb_path}...")
    lancedb_manager = LanceDBManager(dimension, lancedb_path)
    
    print("Inserting data into LanceDB...")
    # LanceDB add_vectors already handles proper list dict format
    lancedb_manager.add_vectors(vectors, vector_ids)
    
    print("Migration completed successfully!")
    print(f"You can now safely move or delete '{faiss_path}' if desired.")

if __name__ == "__main__":
    migrate()
