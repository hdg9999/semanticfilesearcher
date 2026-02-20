import faiss
import numpy as np
import os
import pickle

class VectorDBManager:
    def __init__(self, dimension, index_path="data/vector_index.faiss"):
        self.dimension = dimension
        self.index_path = index_path
        
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            # Check if index is IDMap
            if not isinstance(self.index, faiss.IndexIDMap):
                 # Migration or reset might be needed if type changed.
                 # For now, we assume if it exists it matches the new structure 
                 # or the user accepts a reset (which we will force if incompatible).
                 pass
        else:
            # 内적 (Inner Product) for Cosine Similarity (requires normalized vectors)
            base_index = faiss.IndexFlatIP(dimension)
            # IDMap to manage vector IDs explicitly
            self.index = faiss.IndexIDMap(base_index)

    def add_vectors(self, vectors: np.ndarray, vector_ids: list):
        """벡터와 명시적인 ID를 추가합니다. 벡터는 정규화되어야 합니다."""
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension {vectors.shape[1]} does not match index dimension {self.dimension}")
        if len(vectors) != len(vector_ids):
            raise ValueError("Values and IDs must have the same length")
        
        # Normalize for Cosine Similarity
        faiss.normalize_L2(vectors)
        
        # Add with IDs
        self.index.add_with_ids(vectors.astype('float32'), np.array(vector_ids).astype('int64'))
        self.save()

    def search(self, query_vector: np.ndarray, top_k=50):
        """가장 유사한 벡터의 ID들을 반환합니다."""
        if query_vector.shape[1] != self.dimension:
            raise ValueError(f"Query vector dimension {query_vector.shape[1]} does not match index dimension {self.dimension}")
        
        # Normalize query
        faiss.normalize_L2(query_vector)
        
        distances, indices = self.index.search(query_vector.astype('float32'), top_k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx != -1:
                results.append({
                    "vector_id": int(idx), # This is the ID we added
                    "distance": float(dist)
                })
        return results

    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)

    def delete_vectors_by_ids(self, vector_ids):
        """명시적인 ID 리스트로 벡터를 삭제합니다."""
        if not vector_ids:
            return
        
        ids_to_remove = np.array(vector_ids).astype('int64')
        self.index.remove_ids(ids_to_remove)
        self.save()
