import sys, os
os.environ.pop("SSLKEYLOGFILE", None)  # AhnLab/Banking security OpenSSL Applink crash fix
from PySide6.QtWidgets import QApplication
from core.indexer import SemanticIndexer
from ui.main_window import MainWindow

def main():
    # 1. 인덱서 초기화
    # 주의: 실제 Qwen 모델 로드는 시간이 걸리므로 스플래시 스크린이나 
    # 백그라운드 스레드 처리가 필요할 수 있습니다.
    indexer = SemanticIndexer()
    
    # 2. Qt 앱 실행
    app = QApplication(sys.argv)
    
    # 글로벌 스타일시트 적용
    # 글로벌 스타일시트 적용
    from ui.style_manager import StyleManager
    StyleManager().apply_global_style(app)
    
    window = MainWindow(indexer)
    window.show()
    
    indexer.start_monitoring()
    
    try:
        sys.exit(app.exec())
    finally:
        indexer.stop()

if __name__ == "__main__":
    main()
