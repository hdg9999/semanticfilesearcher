import lancedb
import numpy as np
import os
import pyarrow as pa

class VectorDBManager:
    def __init__(self, dimension, index_path="data/lancedb_store"):
        self.dimension = dimension
        self.index_path = index_path
        self.table_name = "vectors"
        
        # Connect to lancedb directory
        os.makedirs(index_path, exist_ok=True)
        self.db = lancedb.connect(index_path)
        
        if self.table_name in self.db.table_names():
            self.table = self.db.open_table(self.table_name)
        else:
            # Create schema explicitly
            schema = pa.schema([
                pa.field("id", pa.int64()),
                pa.field("vector", pa.list_(pa.float32(), list_size=self.dimension))
            ])
            self.table = self.db.create_table(self.table_name, schema=schema)

    def add_vectors(self, vectors: np.ndarray, vector_ids: list):
        """벡터와 명시적인 ID를 추가합니다. 벡터는 정규화되어야 합니다."""
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension {vectors.shape[1]} does not match index dimension {self.dimension}")
        if len(vectors) != len(vector_ids):
            raise ValueError("Values and IDs must have the same length")
        
        # LanceDB는 cosine 메트릭 설정 시 스스로 정규화 후 연산하므로 명시적인 L2 노멀라이즈 제거
        # Lancedb dict array로 삽입
        data = []
        for vid, vec in zip(vector_ids, vectors):
            data.append({"id": int(vid), "vector": vec.astype('float32').tolist()})
            
        if data:
            self.table.add(data)

    def search(self, query_vector: np.ndarray, top_k=50):
        """가장 유사한 벡터의 ID들을 반환합니다."""
        if query_vector.shape[1] != self.dimension:
            raise ValueError(f"Query vector dimension {query_vector.shape[1]} does not match index dimension {self.dimension}")
            
        # LanceDB 조회 방식: cosine distance를 활용. 
        # 주의: FAISS IP는 코사인 유사도(1에 가까울수록 비슷)를 반환하지만,
        # LanceDB cosine는 코사인 거리(0에 가까울수록 비슷)를 반환합니다.
        # 기존 애플리케이션의 유사도 필터 로직과 호환성을 위해 1 - distance 형태로 반환 (Similarty)
        results = (self.table.search(query_vector[0].astype('float32').tolist())
                   .metric("cosine")
                   .limit(top_k)
                   .to_list())
        
        formatted_results = []
        for res in results:
            # FAISS IP score = 1 - LanceDB cosine distance
            similarity = 1.0 - res["_distance"]
            formatted_results.append({
                "vector_id": res["id"],
                "distance": float(similarity)
            })
            
        # 유사도 내림차순 정렬 (Similarity 가 높은 순서)
        formatted_results.sort(key=lambda x: x["distance"], reverse=True)
        return formatted_results

    def save(self):
        """LanceDB는 Auto-commit이므로 패스합니다."""
        pass

    def delete_vectors_by_ids(self, vector_ids):
        """명시적인 ID 리스트로 벡터를 삭제합니다."""
        if not vector_ids:
            return
        
        ids_str = ", ".join(str(vid) for vid in vector_ids)
        self.table.delete(f"id IN ({ids_str})")
