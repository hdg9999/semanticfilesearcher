from PySide6.QtCore import QThread, Signal
import os
import traceback

class IndexerInitThread(QThread):
    progress = Signal(int)
    status = Signal(str)
    finished_init = Signal(object) # returns indexer instance
    error = Signal(str)

    def run(self):
        try:
            self.status.emit("초기화 환경 구성 중...")
            
            # HuggingFace hub tqdm 패치 (모델 다운로드 모니터링용)
            OriginalTqdm = None
            old_init = None
            old_update = None
            old_close = None
            try:
                from huggingface_hub.utils import tqdm as OriginalTqdm
                
                if OriginalTqdm:
                    thread_instance = self
                    
                    old_init = OriginalTqdm.__init__
                    old_update = OriginalTqdm.update
                    old_close = OriginalTqdm.close
                    
                    def new_init(self, *args, **kwargs):
                        old_init(self, *args, **kwargs)
                        # GUI 환경에서는 기본적으로 disable=True가 되므로 이를 무시하도록 완화
                        desc = kwargs.get('desc', "모델 로드/다운로드 중...")
                        thread_instance.status.emit(desc)
                        
                    def new_update(self, n=1):
                        old_update(self, n)
                        # disable=True라도 시그널은 방출하도록 변경
                        if getattr(self, 'total', None):
                            percent = int((self.n / self.total) * 100)
                            thread_instance.progress.emit(percent)
                            
                    def new_close(self):
                        old_close(self)
                        # disable=True라도 종료 시그널은 방출
                        thread_instance.progress.emit(100)

                    OriginalTqdm.__init__ = new_init
                    OriginalTqdm.update = new_update
                    OriginalTqdm.close = new_close
            except ImportError:
                print("huggingface_hub module not found for tqdm patch")

            self.status.emit("인덱서 및 임베딩 모델 로드 중...")
            from core.indexer import SemanticIndexer
            indexer = SemanticIndexer()
            
            # 패치 복구
            if OriginalTqdm and old_init:
                OriginalTqdm.__init__ = old_init
                OriginalTqdm.update = old_update
                OriginalTqdm.close = old_close
                
            self.finished_init.emit(indexer)
            
        except Exception as e:
            traceback.print_exc()
            self.error.emit(str(e))
            # 패치 롤백
            try:
                if 'OriginalTqdm' in locals() and OriginalTqdm:
                    hf_tqdm_module.tqdm = OriginalTqdm
            except Exception:
                pass


class IndexingWorker(QThread):
    progress = Signal(int, int, str) # current, total, filename
    finished = Signal(int) # total_indexed

    def __init__(self, indexer, folders):
        super().__init__()
        self.indexer = indexer
        self.folders = folders

    def run(self):
        total_files = 0
        for folder in self.folders:
            for root, _, files in os.walk(folder):
                total_files += len(files)
        
        indexed_count = 0
        for folder in self.folders:
            for root, _, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.indexer.scanner.process_file(file_path)
                    indexed_count += 1
                    self.progress.emit(indexed_count, total_files, file)
        
        self.finished.emit(indexed_count)
