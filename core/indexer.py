from core.database.sqlite_manager import DatabaseManager
from core.database.vector_db import VectorDBManager
from core.embedding.qwen_adapter import QwenEmbeddingAdapter
from core.indexing.scanner import FileScanner
from core.indexing.monitor import FileMonitor
from core.tagging.auto_tagger import AutoTagger
from core.tagging.llm_adapters import OllamaAdapter, OpenAIAdapter, GeminiAdapter, HuggingFaceAdapter
from core.config import ConfigManager
from core.indexing.queue_manager import IndexingQueueManager
import os
import threading
import time
from datetime import datetime

class SemanticIndexer:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.config = ConfigManager(os.path.join(data_dir, "config.json"))
        
        # 1. 초기화
        self.embedding = QwenEmbeddingAdapter()
        self.db = DatabaseManager(os.path.join(data_dir, "metadata.db"))
        self.vector_db = VectorDBManager(self.embedding.dimension, os.path.join(data_dir, "vector.faiss"))
        
        # 2. LLM 태거 설정 
        self._init_tagger()
        
        self.scanner = FileScanner(self.embedding, self.db, self.vector_db)
        
        # 3. 큐 관리자 및 워커 스레드 초기화
        self.queue_manager = IndexingQueueManager()
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

        self.monitor = FileMonitor() # Scanner dependency removed
        
        # 초기 저장되어있던 폴더들 모니터링 시작
        for folder in self.config.get_folders():
            if os.path.exists(folder):
                self.monitor.add_path(folder, self._on_change)

    def _init_tagger(self):
        cfg = self.config.get_llm_config()
        provider = cfg.get("provider", "Ollama")
        model = cfg.get("model", "llama3")
        api_key = cfg.get("api_key", "")
        base_url = cfg.get("base_url", "") # base_url 로드
        
        if provider == "OpenAI":
            adapter = OpenAIAdapter(api_key=api_key, model=model, base_url=base_url if base_url else None)
        elif provider == "Gemini":
            adapter = GeminiAdapter(api_key=api_key, model=model)
        elif provider == "HuggingFace":
            adapter = HuggingFaceAdapter(model_path=model)
        else: # Ollama default
            if base_url:
                adapter = OllamaAdapter(model=model, base_url=base_url)
            else:
                adapter = OllamaAdapter(model=model)
            
        self.tagger = AutoTagger(adapter=adapter)
        print(f"Tagger initialized with provider: {provider}, model: {model}")

    def reload_tagger(self):
        print("Reloading tagger...")
        self._init_tagger()

    def index_folder(self, folder_path):
        if folder_path not in self.config.get_folders():
            self.config.add_folder(folder_path)
        self.monitor.add_path(folder_path, self._on_change)
        
        # 비동기 처리를 위해 큐에 추가
        print(f"Queueing initial scan for: {folder_path}")
        # 폴더 내 모든 파일을 순회하며 큐에 추가 (메인 스레드에서 순회는 빠름, 파일 처리가 느림)
        # 파일이 매우 많을 경우 순회 자체도 스레드로 뺄 필요가 있으나, 1차적으로는 이정도로 개선.
        # 더 나은 반응성을 위해 별도 스레드에서 walk 수행 권장.
        threading.Thread(target=self._queue_all_files, args=(folder_path,), daemon=True).start()

    def _queue_all_files(self, folder_path):
        count = 0
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                self.queue_manager.add_task(file_path, "update")
                count += 1
        print(f"Queued {count} files from {folder_path}") 

    def remove_folder(self, folder_path):
        self.config.remove_folder(folder_path)
        self.monitor.remove_path(folder_path)

    def search(self, query, mode="통합 검색", extensions=None, tags=None, tag_logic="AND"):
        # 1. 확장자 필터링 (SQLite에서 미리 처리하거나 후처리 가능)
        # 여기서는 우선 벡터 검색 후 후처리를 수행하거나 상위 레벨에서 필터링합니다.
        
        # 2. 검색 모드에 따른 처리
        # 태그가 제공되면 태그 검색 로직 수행 (검색어 없음)
        if tags and not query:
            results = self.db.search_by_tags(tags, condition=tag_logic)
            return [{"file_path": path, "distance": 0.0} for path in results]

        # 태그와 검색어가 둘 다 있는 경우 (1-3 요구사항: 검색어 + 태그 필터링)
        # 우선 벡터 검색 후 태그로 필터링 (또는 반대) - 우선 벡터 검색 결과를 가져옴
        if mode == "태그 검색":
             # Legacy mode support if any
             if query:
                results = self.db.search_by_tag(query)
                return [{"file_path": path, "distance": 0.0} for path in results]
            
        # 3. 벡터 검색
        query_vec = self.embedding.encode_text(query)
        vector_results = self.vector_db.search(query_vec, top_k=50)
        
        # 4. 후속 필터링 (확장자 등)
        filtered_results = []
        
        # 태그 필터링을 위한 허용 파일 목록 미리 조회 (Query + Tags 경우)
        allowed_files_by_tags = None
        if tags and query:
             allowed_files_by_tags = set(self.db.search_by_tags(tags, condition=tag_logic))

        for res in vector_results:
            path = res['file_path']
            # 파일 존재 여부 확인 (삭제된 파일이 벡터DB에 남아있을 수 있음)
            if not os.path.exists(path):
                continue

            # 태그 필터 적용
            if allowed_files_by_tags is not None:
                if path not in allowed_files_by_tags:
                    continue

            ext = os.path.splitext(path)[1].lower().replace(".", "")
            
            if extensions and ext not in extensions:
                continue
                
            # 이미지/텍스트 모드 필터 (간단 구현)
            if mode == "이미지 검색" and ext not in ["jpg", "jpeg", "png", "bmp", "gif"]:
                continue
            if mode == "텍스트 검색" and ext in ["jpg", "jpeg", "png", "bmp", "gif"]:
                continue
                
            filtered_results.append(res)
            
        return filtered_results

    def _on_change(self, file_path, action):
        # Watchdog 이벤트 -> 우선순위 큐로 전달
        # Watchdog 이벤트 -> 우선순위 큐로 전달
        if action in ["created", "modified"]:
            # 단순 읽기 등으로 인한 중복 감지 방지
            # DB에 저장된 시간과 현재 파일 시간이 같으면 큐에 추가하지 않음
            if os.path.exists(file_path):
                current_mtime = os.path.getmtime(file_path)
                last_modified = datetime.fromtimestamp(current_mtime)
                
                db_metadata = self.db.get_file_metadata(file_path)
                if db_metadata:
                    stored_modified = db_metadata.get('last_modified')
                    # 저장된 시간과 현재 시간이 같으면 무시
                    # (Scanner 내부에서도 체크하지만, 큐 진입 자체를 막기 위함)
                    if str(stored_modified) == str(last_modified):
                        # print(f"Ignored event (Unchanged): {file_path}")
                        return

            self.queue_manager.add_task(file_path, "update")
        elif action == "deleted":
            self.queue_manager.add_task(file_path, "deleted")

    def _worker(self):
        print("Indexing worker started")
        while self.running:
            task = self.queue_manager.get_next_task()
            if task:
                try:
                    self.queue_manager.set_current_task(task)
                    
                    if task.status == "update":
                        # 파일이 존재하는지 확인 (큐 대기 중 삭제되었을 수 있음)
                        if os.path.exists(task.path):
                            print(f"[Worker] Processing update: {task.path}")
                            self.scanner.process_file(task.path)
                            # 태그 생성
                            try:
                                tags = self.tagger.generate_tags(task.path, [tag[0] for tag in self.db.get_all_tags()])
                                for tag in tags:
                                    self.db.link_file_tag(task.path, tag)
                            except Exception as e:
                                print(f"[Worker] Tag generation failed for {task.path}: {e}")
                        else:
                             print(f"[Worker] File not found (skipping): {task.path}")

                    elif task.status == "deleted":
                        print(f"[Worker] Processing delete: {task.path}")
                        self.db.delete_file(task.path)
                        # 벡터 DB 삭제 로직은 별도 구현 필요할 수 있음
                except Exception as e:
                    print(f"[Worker] Error processing {task.path}: {e}")
                finally:
                    self.queue_manager.clear_current_task()
            else:
                time.sleep(0.5) # Idle wait

    def start_monitoring(self):
        self.monitor.start()

    def stop(self):
        self.running = False
        self.monitor.stop()
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)
