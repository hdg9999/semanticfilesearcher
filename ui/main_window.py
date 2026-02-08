from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QListWidget, QLabel, 
                             QFileDialog, QListWidgetItem, QMessageBox, QProgressBar,
                             QComboBox, QScrollArea, QFrame, QSplitter, QApplication)
from PySide6.QtCore import Qt, QSize, QUrl, QTimer
from PySide6.QtGui import QFont, QAction, QDesktopServices, QIcon, QPixmap
from ui.workers import IndexingWorker
from ui.settings_dialog import SettingsDialog
from ui.components.result_item import FileResultWidget
from ui.components.detail_pane import DetailPane
from ui.components.badged_button import BadgedButton
from ui.components.tag_input import TagInputWidget
from ui.components.tag_input import TagInputWidget
from ui.components.tag_input import TagInputWidget
from ui.components.sidebar import FileSidebar
from ui.components.path_bar import PathBar
import os

class MainWindow(QMainWindow):
    def __init__(self, indexer):
        super().__init__()
        self.indexer = indexer
        self.setWindowTitle("Semantic File Searcher")
        
        # Load Icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icon.png")
        if os.path.exists(icon_path):
             self.setWindowIcon(QIcon(icon_path))
             
        self.resize(1200, 850)
        
        # Load component style
        from ui.style_manager import StyleManager
        self.style_manager = StyleManager()
        # Initial theme application will be done after UI initialization

        # Load specific component style for main window customization if needed
        style = self.style_manager.get_component_style("main_window")
        if style:
            self.setStyleSheet(self.styleSheet() + "\n" + style)

        self.completer = None
        self.tag_colors = {} # Initialize tag_colors dictionary
        self.worker = None
        self.view_mode = "list"
        self.selected_item = None # Currently selected FileResultWidget
        self.current_context = "search"
        self.current_directory = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 상단 도구 모음 및 검색 바 영역
        top_container = QWidget()
        top_container.setObjectName("topContainer")
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
        tag_container.setObjectName("tagContainer")
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



        # 메인 좌우 분할 (사이드바 | 콘텐츠)
        self.main_h_splitter = QSplitter(Qt.Horizontal)
        self.main_h_splitter.setHandleWidth(1) # Thin divider
        
        # 1. 좌측 사이드바
        self.sidebar = FileSidebar()
        self.sidebar.folder_selected.connect(self.on_folder_selected)
        self.main_h_splitter.addWidget(self.sidebar)
        
        # 2. 우측 콘텐츠 영역
        right_content_widget = QWidget()
        right_content_layout = QVBoxLayout(right_content_widget)
        right_content_layout.setContentsMargins(0, 0, 0, 0)
        right_content_layout.setSpacing(0)
        
        # 2.5. 경로 표시줄 (Path Bar)
        self.path_bar = PathBar()
        self.path_bar.path_changed.connect(self.load_directory)
        self.path_bar.refresh_clicked.connect(lambda: self.load_directory(self.path_bar.current_path))
        right_content_layout.addWidget(self.path_bar)
        
        # 3행: 뷰 모드 컨트롤 바 (검색 모드 아래, 결과창 위)
        control_container = QWidget()
        control_container.setObjectName("controlContainer")
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
        

        
        right_content_layout.addWidget(control_container) # Add to right content instead of main_layout

        # 중간 영역 (Splitter 사용)
        self.content_splitter = QSplitter(Qt.Horizontal)
        
        # 결과 리스트 (Scroll Area 사용)
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("resultArea")
        self.scroll_area.setWidgetResizable(True)
        
        self.result_container = QWidget()
        self.result_container.setObjectName("resultContainer")
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
        
        right_content_layout.addWidget(self.content_splitter, 1) # Add stretch factor to expand
        
        self.main_h_splitter.addWidget(right_content_widget)
        self.main_h_splitter.setStretchFactor(1, 1) # Give right side more space
        self.main_h_splitter.setSizes([250, 950]) # Sidebar width
        
        main_layout.addWidget(self.main_h_splitter, 1)


        # 하단 상태 바
        status_container = QWidget()
        status_container.setObjectName("statusContainer")
        status_layout = QHBoxLayout(status_container) # QV -> QH for button
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setFixedWidth(200) # Fixed width
        status_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("준비 완료")
        self.status_label.setObjectName("statusLabel")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        
        # Bottom Queue Button removed (moved to header)
        # self.queue_btn = QPushButton("대기열: 0")
        # ...
        
        main_layout.addWidget(status_container)

        self._create_menu_bar()
        self.refresh_tag_completer() # Initialize completer
        
        # Apply theme after all UI components are initialized
        self.apply_theme("dark")
        
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
        if self.current_context == 'directory' and self.current_directory:
            self.load_directory(self.current_directory)
        else:
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
        
        # Update Context and PathBar
        self.current_context = 'search'
        self.current_directory = None
        if hasattr(self, 'path_bar'):
            # os.path.normpath might mess up the display string if it looks like a path, but for simple text it's fine.
            # We bypass set_path's normpath if needed, but let's try using set_path for consistency in breadcrumbs.
            self.path_bar.set_path(f"'{query}' 검색 결과")
        
        # 결과 렌더링
        # 뷰 모드에 따라 컨테이너 및 레이아웃 설정
        from ui.components.flow_layout import FlowLayout

        new_container = QWidget()
        new_container.setObjectName("resultContainer")
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
            tags = res.get('tags', [])
            widget = FileResultWidget(path, view_mode=self.view_mode, tags=tags)
            widget.clicked.connect(self.on_file_clicked)
            widget.double_clicked.connect(self.on_file_double_clicked)
            widget.manage_tags_requested.connect(self.open_file_tag_dialog)
            widget.tag_clicked.connect(self.add_tag_to_search)
            self.result_layout.addWidget(widget)
            
        self.status_label.setText(f"검색 완료: {len(results)}개의 결과")
        self.selected_item = None # Reset selection on new search

    def add_tag_to_search(self, tag_name):
        self.tag_input.add_tag(tag_name)
        # Optional: Scroll to top or give feedback?
        # For now, just add it. The user can press enter to search again with the new tag.

    def toggle_detail_pane(self, checked):
        self.detail_pane.setVisible(checked)

    def on_file_clicked(self, path):
        try:
            # Handle visual selection
            sender = self.sender()
            # print(f"File clicked: {path}, sender: {sender}")
            
            if isinstance(sender, FileResultWidget):
                 if self.selected_item and self.selected_item != sender:
                     self.selected_item.set_selected(False)
                 
                 self.selected_item = sender
                 self.selected_item.set_selected(True)
    
                 # Update Detail Pane
                 try:
                     tags = self.indexer.db.get_tags_for_file(path)
                 except Exception as e:
                     print(f"Error fetching tags: {e}")
                     tags = []
                     
                 # Get icon from the widget safe access
                 icon = None
                 if hasattr(sender, 'icon_label') and sender.icon_label:
                     icon = sender.icon_label.pixmap()
                 
                 self.detail_pane.update_info(path, tags, icon)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error in on_file_clicked: {e}")

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

        # 편집 메뉴
        edit_menu = menubar.addMenu("편집(&E)")
        
        # 테마 서브 메뉴
        theme_menu = edit_menu.addMenu("테마(&T)")
        
        dark_action = QAction("다크 모드", self)
        dark_action.triggered.connect(lambda: self.apply_theme("dark"))
        theme_menu.addAction(dark_action)
        
        light_action = QAction("라이트 모드", self)
        light_action.triggered.connect(lambda: self.apply_theme("light"))
        theme_menu.addAction(light_action)

    def show_settings(self):
        dialog = SettingsDialog(self.indexer, self)
        dialog.exec()
        # 설정 창이 닫힌 후 태그 정보(색상 등)가 변경되었을 수 있으므로 갱신
        self.refresh_tag_completer()

    def apply_theme(self, theme_name):
        self.style_manager.apply_global_style(QApplication.instance(), theme_name)
        self.update_icons()
        
        # Force update tag input colors if needed (though predominantly handled by QSS)
        # Re-apply current search to refresh result widgets with new styles
        self.perform_search()

    def update_icons(self):
        suffix = self.style_manager.get_icon_suffix()
        
        # Update Queue Button
        self.queue_btn.setIcon(QIcon(f"ui/resources/icons/queue{suffix}.svg"))
        
        # Update View Mode Buttons
        self.view_list_btn.setIcon(QIcon(f"ui/resources/icons/list_view{suffix}.svg"))
        self.view_icon_btn.setIcon(QIcon(f"ui/resources/icons/icon_view{suffix}.svg"))
        
        # Update Sidebar Toggle Button
        self.toggle_detail_btn.setIcon(QIcon(f"ui/resources/icons/sidebar_toggle{suffix}.svg"))

        # Update PathBar Icons
        if hasattr(self, 'path_bar'):
            self.path_bar.update_icons(suffix)

    def on_folder_selected(self, path):
        self.load_directory(path)

    def load_directory(self, path):
        if not os.path.exists(path) or not os.path.isdir(path):
            return
        
        # Normalize path casing/symlinks for consistency with DB
        path = os.path.realpath(path)

        self.status_label.setText(f"폴더 로드 중: {path}")
        
        self.current_context = 'directory'
        self.current_directory = path
        
        self.path_bar.set_path(path)
        # Sync Sidebar (block signals to avoid recursion if needed, but sidebar emits on click, not set current)
        self.sidebar.select_path(path)
        
        # Reset selection to avoid holding reference to deleted widgets
        self.selected_item = None
        
        # Clear current results
        # Re-use result container setup from perform_search
        from ui.components.flow_layout import FlowLayout
        new_container = QWidget()
        new_container.setObjectName("resultContainer")
        
        if self.view_mode == "list":
            self.result_layout = QVBoxLayout(new_container)
            self.result_layout.setAlignment(Qt.AlignTop)
        else:
            self.result_layout = FlowLayout(new_container)
            
        self.scroll_area.setWidget(new_container)
        self.result_container = new_container
        
        # Fetch files
        try:
            # 1. Scanner files (Disk)
            with os.scandir(path) as entries:
                disk_files = [e for e in entries if e.is_file()]
                
            # 2. Build tag/status map from DB
            # We use LIKE queries to cover both forward and backward slash variants in DB
            db_map = {} # normcase_path -> tags list
            
            # Prepare prefixes
            # Ensure trailing slash to match only children/descendants (though we filter later)
            path_win = path.rstrip(os.sep) + os.sep
            path_unix = path.replace('\\', '/').rstrip('/') + '/'
            
            # Query
            query = """
                SELECT f.file_path, t.name, t.color 
                FROM files f
                LEFT JOIN file_tags ft ON f.id = ft.file_id
                LEFT JOIN tags t ON ft.tag_id = t.id
                WHERE f.file_path LIKE ? OR f.file_path LIKE ?
            """
            
            with self.indexer.db._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (f"{path_win}%", f"{path_unix}%"))
                rows = cursor.fetchall()
                
                # Process DB results
                for f_path, t_name, t_color in rows:
                    # Normalize DB path to compare with Disk path
                    # normcase handles case-insensitivity on Windows and slash normalization
                    norm_path = os.path.normcase(os.path.normpath(f_path))
                    
                    if norm_path not in db_map:
                        db_map[norm_path] = {'tags': [], 'registered': True}
                    
                    if t_name: # If tag exists
                        db_map[norm_path]['tags'].append((t_name, t_color))

            # 3. Create Widgets
            for entry in disk_files:
                file_path = entry.path
                norm_path = os.path.normcase(os.path.normpath(file_path))
                
                info = db_map.get(norm_path, {'tags': [], 'registered': False})
                is_registered = info.get('registered', False)
                tags = info.get('tags', [])
                
                # Create Widget
                widget = FileResultWidget(file_path, view_mode=self.view_mode, tags=tags)
                
                if not is_registered:
                     widget.set_unregistered_status()

                widget.clicked.connect(self.on_file_clicked)
                widget.double_clicked.connect(self.on_file_double_clicked)
                widget.manage_tags_requested.connect(self.open_file_tag_dialog)
                widget.tag_clicked.connect(self.add_tag_to_search)
                self.result_layout.addWidget(widget)

            self.status_label.setText(f"폴더 로드 완료: {len(disk_files)}개 파일")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"폴더를 열 수 없습니다: {e}")

