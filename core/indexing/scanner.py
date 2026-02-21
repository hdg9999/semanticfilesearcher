import os
import fitz  # PyMuPDF
from docx import Document
from PIL import Image
from datetime import datetime

class FileScanner:
    def __init__(self, embedding_adapter, db_manager, vector_db_manager=None):
        self.embedding_adapter = embedding_adapter
        self.db_manager = db_manager
        self.vector_db_manager = vector_db_manager
        self.supported_extensions = {
            'text': ['.txt', '.md', '.py', '.c', '.cpp', '.h', '.java', '.js', '.html', '.css'],
            'document': ['.pdf', '.docx'],
            'image': ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        }

    def scan_directory(self, directory_path):
        """디렉토리를 스캔하여 인덱싱 대상을 찾습니다."""
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                self.process_file(file_path)

    def process_file(self, file_path):
        """단일 파일을 처리하여 DB에 저장하고 임베딩을 생성합니다."""
        # Normalize path to use OS separator (e.g. Backslash on Windows)
        file_path = os.path.normpath(file_path)
        
        ext = os.path.splitext(file_path)[1].lower()
        mtime = os.path.getmtime(file_path)
        last_modified = datetime.fromtimestamp(mtime)

        # 0. 변경 여부 확인 (중복 인덱싱 방지)
        db_metadata = self.db_manager.get_file_metadata(file_path)
        if db_metadata:
            stored_last_modified_str = db_metadata.get("last_modified")
            # SQLite stores datetime as string usually, need to parse if it's string
            # But here let's rely on strict comparison or string comparison if format is consistent
            # Python sqlite3 adapter might return datetime object if configured, but let's be safe.
            # Assuming standard string format "YYYY-MM-DD HH:MM:SS..."
            
            # Simple string comparison might work if formats are identical.
            # Let's try to parse if needed, or compare string representation of current time.
            # Actually, `upsert_file` passes a datetime object. SQLite adapter handles conversion.
            # When reading back, it might be string.
            
            # Let's simplify: Compare timestamp if possible or string. 
            # Ideally we check if abs(stored - current) < threshold.
            # For now, let's just convert current to string and compare, or parse stored.
            
            # Note: sqlite_manager uses `last_modified` from arguments directly.
            # Let's fetch what we just read.
            pass

        # To avoid timezone/format complexity, let's re-fetch the robust way or just do a quick check.
        # If we use string comparison, we need to ensure format matches DB's default.
        # Let's compare timestamps.
        
        should_process = True
        if db_metadata:
             stored_modified = db_metadata['last_modified']
             # If stored_modified is string, parse it.
             if isinstance(stored_modified, str):
                 try:
                    # SQLite default format: "YYYY-MM-DD HH:MM:SS.mmmmmm" or similar
                    stored_dt = datetime.fromisoformat(stored_modified)
                    # OR specific format? sqlite3 defaults to "YYYY-MM-DD HH:MM:SS.uuuuuu" usually
                    # Let's try flexible parsing or string matching.
                    # Since we are writing `last_modified` (datetime) into DB, 
                    # check how it's stored. `upsert_file` takes `last_modified`.
                    pass
                 except:
                    pass
             
             # Actually, simpler: Let's assume strict string equality if we format it same way,
             # OR just proceed if not sure. 
             # But better: Check if file size also changed? (Not stored currently).
             
             # Let's proceed with a standard comparison allowing for small drift or string match.
             # If `stored_modified` == `str(last_modified)`, skip.
             if str(stored_modified) == str(last_modified):
                 should_process = False
                 print(f"Skipped (Unchanged): {file_path}")

        if should_process:
            # 1. 텍스트/이미지 추출 및 임베딩 생성
            embeddingsList = []
            if self._is_supported(ext, 'text') or self._is_supported(ext, 'document'):
                text = self.extract_text(file_path)
                if text:
                    from core.indexing.chunker import TextChunker
                    chunker = TextChunker()
                    chunks = chunker.split_text(text)
                    
                    if chunks:
                        # 배치 단위 처리를 통해 VRAM 초과 방지
                        batch_size = 8
                        for i in range(0, len(chunks), batch_size):
                            batch = chunks[i:i+batch_size]
                            try:
                                emb = self.embedding_adapter.encode_text(batch)
                                embeddingsList.extend(emb)
                            except Exception as e:
                                print(f"Error encoding text batch for {file_path}: {e}")
            elif self._is_supported(ext, 'image'):
                try:
                    emb = self.embedding_adapter.encode_image(file_path)
                    if emb is not None and len(emb) > 0:
                        embeddingsList.extend(emb)
                except Exception as e:
                    print(f"Error encoding image {file_path}: {e}")
    
            # 2. DB 업데이트: 항상 수행 (메타데이터/파일명 검색 등)
            file_id = self.db_manager.upsert_file(file_path, last_modified)
            
            # 3. Vector DB 업데이트
            if len(embeddingsList) > 0 and self.vector_db_manager:
                import numpy as np
                # 3-1. 기존 벡터 삭제 (파일 수정 시)
                old_vector_ids = self.db_manager.get_vector_ids(file_id)
                if old_vector_ids:
                    self.vector_db_manager.delete_vectors_by_ids(old_vector_ids)
                    self.db_manager.delete_vector_ids(old_vector_ids)

                # 3-2. 새 벡터 ID 발급
                new_vector_ids = []
                for _ in range(len(embeddingsList)):
                    new_vector_ids.append(self.db_manager.allocate_vector_id(file_id))
                
                # 3-3. Vector DB에 추가
                self.vector_db_manager.add_vectors(np.array(embeddingsList), new_vector_ids)
                print(f"Indexed (with {len(new_vector_ids)} embeddings): {file_path}")
            else:
                print(f"Indexed (metadata only): {file_path}")

    def extract_text(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext in self.supported_extensions['text']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            elif ext == '.pdf':
                doc = fitz.open(file_path)
                return " ".join([page.get_text() for page in doc])
            elif ext == '.docx':
                doc = Document(file_path)
                return " ".join([p.text for p in doc.paragraphs])
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
        return ""

    def _is_supported(self, ext, category):
        return ext in self.supported_extensions.get(category, [])
