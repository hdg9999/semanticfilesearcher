import sys, os
os.environ.pop("SSLKEYLOGFILE", None)  # AhnLab/Banking security OpenSSL Applink crash fix
from PySide6.QtWidgets import QApplication
from ui.splash_screen import SplashScreen
from ui.workers import IndexerInitThread
from ui.main_window import MainWindow

def main():
    # 1. Qt 앱 초기화
    app = QApplication(sys.argv)
    
    # 글로벌 스타일시트 적용
    from ui.style_manager import StyleManager
    StyleManager().apply_global_style(app)
    
    # 2. 스플래시 스크린 표시
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        splash_img = os.path.join(sys._MEIPASS, "assets", "splash image.png")
    else:
        splash_img = os.path.join(os.path.dirname(__file__), "assets", "splash image.png")
        
    splash = SplashScreen(splash_img)
    splash.show()
    
    # 참조 유지를 위한 딕셔너리
    app_data = {}
    
    def on_init_finished(indexer):
        splash.update_status("초기화 완료, 메인 화면 준비 중...")
        splash.update_progress(100)
        
        # 3. 메인 화면 띄우기
        window = MainWindow(indexer)
        app_data['window'] = window
        window.show()
        
        indexer.start_monitoring()
        splash.close()
        
    def on_init_error(err_msg):
        splash.update_status(f"오류 발생: {err_msg}")
        print(f"Error during initialization: {err_msg}")
        
    # 4. 백그라운드 초기화 스레드 시작
    init_thread = IndexerInitThread()
    init_thread.progress.connect(splash.update_progress)
    init_thread.status.connect(splash.update_status)
    init_thread.finished_init.connect(on_init_finished)
    init_thread.error.connect(on_init_error)
    
    app_data['init_thread'] = init_thread
    init_thread.start()
    
    try:
        sys.exit(app.exec())
    finally:
        window = app_data.get('window')
        if window and hasattr(window, 'indexer'):
            window.indexer.stop()

if __name__ == "__main__":
    main()
