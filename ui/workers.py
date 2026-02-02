from PySide6.QtCore import QThread, Signal
import os

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
