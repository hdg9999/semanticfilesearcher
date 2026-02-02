import faiss
import numpy as np
import os
import pickle

class VectorDBManager:
    def __init__(self, dimension, index_path="data/vector_index.faiss"):
        self.dimension = dimension
        self.index_path = index_path
        self.metadata_path = index_path + ".meta"
        
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            with open(self.metadata_path, 'rb') as f:
                self.file_ids = pickle.load(f)
        else:
            # L2 distance index (IndexFlatL2)
            self.index = faiss.IndexFlatL2(dimension)
            self.file_ids = [] # index의 순서와 대응하는 file_id 또는 file_path 리스트

    def add_vectors(self, vectors: np.ndarray, file_path_list: list):
        """벡터와 그에 대응하는 파일 경로 리스트를 추가합니다."""
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension {vectors.shape[1]} does not match index dimension {self.dimension}")
        
        self.index.add(vectors.astype('float32'))
        self.file_ids.extend(file_path_list)
        self.save()

    def search(self, query_vector: np.ndarray, top_k=10):
        """가장 유사한 벡터의 파일 경로들을 반환합니다."""
        if query_vector.shape[1] != self.dimension:
            raise ValueError(f"Query vector dimension {query_vector.shape[1]} does not match index dimension {self.dimension}")
        
        distances, indices = self.index.search(query_vector.astype('float32'), top_k)
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx != -1 and idx < len(self.file_ids):
                results.append({
                    "file_path": self.file_ids[idx],
                    "distance": float(dist)
                })
        return results

    def save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.file_ids, f)

    def delete_by_index(self, indices_to_remove):
        # IndexFlatL2는 직접적인 삭제가 비효율적일 수 있으므로 
        # 실제 구현에서는 ID 맵핑이나 다른 Index 타입을 고려할 수 있습니다.
        # 여기서는 단순화를 위해 생략하거나 전체 재계산을 고려합니다.
        pass
