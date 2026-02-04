from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QListWidget, QLabel, 
                             QFileDialog, QListWidgetItem, QMessageBox, QProgressBar,
                             QComboBox, QScrollArea, QFrame, QSplitter)
from PySide6.QtCore import Qt, QSize, QUrl, QTimer
from PySide6.QtGui import QFont, QAction, QDesktopServices, QIcon, QPixmap
from ui.workers import IndexingWorker
from ui.settings_dialog import SettingsDialog
from ui.components.result_item import FileResultWidget
from ui.components.detail_pane import DetailPane
from ui.components.badged_button import BadgedButton
from ui.components.tag_input import TagInputWidget
import os

class MainWindow(QMainWindow):
    def __init__(self, indexer):
        super().__init__()
        self.indexer = indexer
        self.setWindowTitle("Semantic File Searcher")
        self.resize(1200, 850)
        
        self.completer = None
        self.tag_colors = {} # Initialize tag_colors dictionary
        self.worker = None
        self.view_mode = "list"
        self.selected_item = None # Currently selected FileResultWidget

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 상단 도구 모음 및 검색 바 영역
        top_container = QWidget()
        top_container.setStyleSheet("background-color: #1e1e1e; border-bottom: 1px solid #333333;")
        top_layout = QVBoxLayout(top_container)
        top_layout.setContentsMargins(20, 10, 20, 10)

        # 1행: 타이틀 및 작업 버튼
        header_layout = QHBoxLayout()
        title_label = QLabel("Semantic Search")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # 대기열 버튼 (헤더 우측 상단으로 이동)
        self.queue_btn = BadgedButton(QIcon("ui/resources/icons/queue_white.svg"))
        self.queue_btn.setFixedSize(40, 40)
        self.queue_btn.setIconSize(QSize(24, 24))
        self.queue_btn.clicked.connect(self.show_queue_status)
        header_layout.addWidget(self.queue_btn)
        
        top_layout.addLayout(header_layout)

        # 2행: 검색 바 및 필터
        search_layout = QHBoxLayout()
        
        self.search_mode = QComboBox()
        self.search_mode.addItems(["통합 검색", "텍스트 검색", "이미지 검색"])
        self.search_mode.setFixedWidth(120)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색어를 입력하세요...")
        self.search_input.returnPressed.connect(self.perform_search)
        
        self.ext_filter = QLineEdit()
        self.ext_filter.setPlaceholderText("확장자 필터 (예: txt, pdf)")
        self.ext_filter.setFixedWidth(150)
        
        self.clear_ext_btn = QPushButton("✕")
        self.clear_ext_btn.setFixedWidth(30)
        self.clear_ext_btn.clicked.connect(lambda: self.ext_filter.clear())
        
        search_layout.addWidget(self.search_mode)
        search_layout.addWidget(self.search_input, stretch=1)
        search_layout.addWidget(self.ext_filter)
        search_layout.addWidget(self.clear_ext_btn)
        top_layout.addLayout(search_layout)
        
        main_layout.addWidget(top_container)

        # 2.5행: 태그 검색 바 (새로 추가)
        tag_container = QWidget()
        tag_container.setStyleSheet("background-color: #1e1e1e; border-bottom: 1px solid #333333;")
        tag_layout = QHBoxLayout(tag_container)
        tag_layout.setContentsMargins(20, 5, 20, 10)
        
        self.tag_logic = QComboBox()
        self.tag_logic.addItems(["AND", "OR"])
        self.tag_logic.setFixedWidth(80)
        self.tag_logic.setToolTip("태그 검색 조건 (AND: 모두 포함, OR: 하나라도 포함)")
        
        self.tag_input = TagInputWidget()
        self.tag_input.return_pressed.connect(self.perform_search)
        
        tag_layout.addWidget(self.tag_logic)
        tag_layout.addWidget(self.tag_input, 1) # Add stretch factor 1
        
        # Insert tag container into main layout (using insertWidget or just add since top_container is added)
        # But main_layout is vertical. So add it after top_container.
        # But top_container was already added. I can't easily insert into main_layout in the middle of this function if I just append.
        # Wait, I am editing __init__. 'main_layout.addWidget(top_container)' was at line 78.
        # So I will just replace the block including 78.
        
        main_layout.addWidget(tag_container)

        # 3행: 뷰 모드 컨트롤 바 (검색 모드 아래, 결과창 위)
        control_container = QWidget()
        control_layout = QHBoxLayout(control_container)
        control_layout.setContentsMargins(20, 5, 20, 5)
        
        self.view_list_btn = QPushButton()
        self.view_list_btn.setIcon(QIcon("ui/resources/icons/list_view_white.svg"))
        self.view_list_btn.setCheckable(True)
        self.view_list_btn.setFixedSize(32, 32)
        self.view_list_btn.setToolTip("목록형 보기")
        
        self.view_icon_btn = QPushButton()
        self.view_icon_btn.setIcon(QIcon("ui/resources/icons/icon_view_white.svg"))
        self.view_icon_btn.setCheckable(True)
        self.view_list_btn.setChecked(True) # Default
        self.view_icon_btn.setFixedSize(32, 32)
        self.view_icon_btn.setToolTip("아이콘형 보기")
        
        self.view_list_btn.clicked.connect(lambda: self.set_view_mode("list"))
        self.view_icon_btn.clicked.connect(lambda: self.set_view_mode("icon"))
        
        
        # Detail Pane Toggle Button
        self.toggle_detail_btn = QPushButton()
        self.toggle_detail_btn.setIcon(QIcon("ui/resources/icons/sidebar_toggle_white.svg"))
        self.toggle_detail_btn.setCheckable(True)
        self.toggle_detail_btn.setChecked(True)
        self.toggle_detail_btn.clicked.connect(self.toggle_detail_pane)
        self.toggle_detail_btn.setFixedSize(32, 32)
        self.toggle_detail_btn.setToolTip("상세 패널 토글")
        
        control_layout.addWidget(self.view_list_btn)
        control_layout.addWidget(self.view_icon_btn)
        control_layout.addWidget(self.toggle_detail_btn) # Add toggle button
        control_layout.addStretch()
        
        main_layout.addWidget(control_container)

        # 중간 영역 (Splitter 사용)
        self.content_splitter = QSplitter(Qt.Horizontal)
        
        # 결과 리스트 (Scroll Area 사용)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background-color: #252526;")
        
        self.result_container = QWidget()
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.result_container)
        
        self.content_splitter.addWidget(self.scroll_area)
        
        # 상세 정보 패널
        self.detail_pane = DetailPane()
        self.content_splitter.addWidget(self.detail_pane)
        
        # 초기 비율 설정 (9:1)
        self.content_splitter.setStretchFactor(0, 9)
        # 초기 비율 설정 (9:1)
        self.content_splitter.setStretchFactor(0, 9)
        self.content_splitter.setStretchFactor(1, 1)
        self.content_splitter.setSizes([900, 300]) # Explicitly set initial sizes
        
        main_layout.addWidget(self.content_splitter, 1) # Add stretch factor to expand


        # 하단 상태 바
        status_container = QWidget()
        status_container.setStyleSheet("background-color: #1e1e1e; border-top: 1px solid #333333;")
        status_layout = QHBoxLayout(status_container) # QV -> QH for button
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setFixedWidth(200) # Fixed width
        status_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("준비 완료")
        self.status_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        
        # Bottom Queue Button removed (moved to header)
        # self.queue_btn = QPushButton("대기열: 0")
        # ...
        
        main_layout.addWidget(status_container)

        self._create_menu_bar()
        self.refresh_tag_completer() # Initialize completer
        self.check_initial_indexing()
        
        # 큐 상태 폴링 타이머
        self.queue_timer = QTimer(self)
        self.queue_timer.timeout.connect(self.update_queue_status)
        self.queue_timer.start(500) # 0.5초마다 갱신

    def update_queue_status(self):
        # Indexer가 초기화되지 않았거나 큐 매니저가 없으면 패스
        if hasattr(self.indexer, 'queue_manager'):
            size = self.indexer.queue_manager.get_queue_size()
            self.queue_btn.set_badge_count(size)

    def show_queue_status(self):
        from ui.queue_dialog import QueueStatusDialog
        dlg = QueueStatusDialog(self.indexer.queue_manager, self)
        dlg.exec()

    def set_view_mode(self, mode):
        self.view_mode = mode
        self.view_list_btn.setChecked(mode == "list")
        self.view_icon_btn.setChecked(mode == "icon")
        self.perform_search() # 현재 검색어로 다시 그리기

    def perform_search(self):
        query = self.search_input.text()
        if not query: return
        
        mode = self.search_mode.currentText()
        exts = [e.strip().lower() for e in self.ext_filter.text().split(",") if e.strip()]
        
        self.status_label.setText(f"검색 중: {query}...")
        
        tags = self.tag_input.get_tags()
        tag_logic = self.tag_logic.currentText()
        
        results = self.indexer.search(query, mode=mode, extensions=exts, tags=tags, tag_logic=tag_logic)
        
        # 결과 렌더링
        # 뷰 모드에 따라 컨테이너 및 레이아웃 설정
        from ui.components.flow_layout import FlowLayout

        new_container = QWidget()
        if self.view_mode == "list":
            self.result_layout = QVBoxLayout(new_container)
            self.result_layout.setAlignment(Qt.AlignTop)
        else:
            self.result_layout = FlowLayout(new_container)
            
        # 기존 스크롤 영역 위젯 교체 (자동으로 이전 위젯은 삭제됨)
        self.scroll_area.setWidget(new_container)
        self.result_container = new_container # 참조 업데이트
        
        for res in results:
            path = res['file_path']
            widget = FileResultWidget(path, view_mode=self.view_mode)
            widget.clicked.connect(self.on_file_clicked)
            widget.double_clicked.connect(self.on_file_double_clicked)
            widget.manage_tags_requested.connect(self.open_file_tag_dialog)
            self.result_layout.addWidget(widget)
            
        self.status_label.setText(f"검색 완료: {len(results)}개의 결과")
        self.selected_item = None # Reset selection on new search

    def toggle_detail_pane(self, checked):
        self.detail_pane.setVisible(checked)

    def on_file_clicked(self, path):
        # Handle visual selection
        sender = self.sender()
        if isinstance(sender, FileResultWidget):
             if self.selected_item:
                 self.selected_item.set_selected(False)
             
             self.selected_item = sender
             self.selected_item.set_selected(True)

             # Update Detail Pane
             tags = self.indexer.db.get_tags_for_file(path)
             # Get icon from the widget
             icon = sender.icon_label.pixmap() if hasattr(sender, 'icon_label') and hasattr(sender.icon_label, 'pixmap') else None
             self.detail_pane.update_info(path, tags, icon)

    def open_file_tag_dialog(self, path):
        from ui.tag_dialog import TagSelectionDialog
        dlg = TagSelectionDialog(self.indexer, path, self)
        if dlg.exec():
            # 태그 변경 후 상세 정보 패널 갱신 (현재 선택된 파일이라면)
            if self.detail_pane.path_label.text() == path:
                 self.on_file_clicked(path)
            # Update tag completer if new tags were added
            self.refresh_tag_completer()

    def refresh_tag_completer(self):
        tags = self.indexer.db.get_all_tags()
        # tags is list of (name, color)
        tag_names = [t[0] for t in tags]
        self.tag_input.set_completer_items(tag_names)
        self.tag_colors = {t[0]: t[1] for t in tags} # Update instance variable
        self.tag_input.set_tag_colors(self.tag_colors) # Pass to TagInputWidget

    def on_file_double_clicked(self, path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def check_initial_indexing(self):
        if not self.indexer.config.get_folders():
            reply = QMessageBox.question(self, "초기 인덱싱 권장", 
                                       "다운로드, 문서, 사진 폴더를 인덱싱하시겠습니까?\n내용 검색을 위해 초기 인덱싱이 권장됩니다.",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                user_dirs = [
                    os.path.join(os.path.expanduser("~"), "Downloads"),
                    os.path.join(os.path.expanduser("~"), "Documents"),
                    os.path.join(os.path.expanduser("~"), "Pictures")
                ]
                valid_dirs = [d for d in user_dirs if os.path.exists(d)]
                self.start_background_indexing(valid_dirs)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "인덱싱할 폴더 선택")
        if folder:
            self.start_background_indexing([folder])

    def start_background_indexing(self, folders):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "경고", "이미 인덱싱 작업이 진행 중입니다.")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("인덱싱 시작 중...")
        
        for f in folders:
            self.indexer.index_folder(f)

        self.worker = IndexingWorker(self.indexer, folders)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_indexing_finished)
        self.worker.start()

    def update_progress(self, current, total, filename):
        percent = int((current / total) * 100) if total > 0 else 0
        self.progress_bar.setValue(percent)
        self.status_label.setText(f"처리 중 ({current}/{total}): {os.path.basename(filename)}")

    def on_indexing_finished(self, total):
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"인덱싱 완료: 총 {total}개 파일")
        QMessageBox.information(self, "완료", f"{total}개의 파일 인덱싱이 완료되었습니다.")

    def _create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("파일(&F)")
        
        settings_action = QAction("설정(&S)", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        exit_action = QAction("종료(&X)", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def show_settings(self):
        dialog = SettingsDialog(self.indexer, self)
        dialog.exec()
        # 설정 창이 닫힌 후 태그 정보(색상 등)가 변경되었을 수 있으므로 갱신
        self.refresh_tag_completer()
