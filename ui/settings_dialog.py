from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QWidget, QLabel, QLineEdit, QPushButton, QComboBox, 
                             QFormLayout, QListWidget, QListWidgetItem, QMessageBox, QFileDialog, QSizePolicy)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor

class SettingsDialog(QDialog):
    def __init__(self, indexer, parent=None):
        super().__init__(parent)
        self.indexer = indexer
        self.setWindowTitle("설정")
        self.resize(550, 450)
        
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        # 탭 생성
        self.tabs.addTab(self._create_llm_tab(), "LLM 설정")
        self.tabs.addTab(self._create_folder_tab(), "폴더 관리")
        self.tabs.addTab(self._create_tag_tab(), "태그 관리")
        
        self.layout.addWidget(self.tabs)
        
        # 하단 버튼
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self.accept)
        close_btn = QPushButton("닫기")
        close_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(close_btn)
        self.layout.addLayout(btn_layout)

    def _create_llm_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        
        self.llm_provider = QComboBox()
        self.llm_provider.addItems(["Ollama", "OpenAI", "Gemini", "HuggingFace"])
        
        self.llm_model = QLineEdit()
        self.llm_model.setPlaceholderText("예: llama3, gpt-4o-mini...")
        
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        
        self.base_url = QLineEdit()
        self.base_url.setPlaceholderText("선택 사항 (예: http://localhost:11434)")
        
        cfg = self.indexer.config.get_llm_config()
        
        layout.addRow("LLM 제공자:", self.llm_provider)
        self.llm_provider.setCurrentText(cfg.get("provider", "Ollama"))
        
        layout.addRow("모델명:", self.llm_model)
        self.llm_model.setText(cfg.get("model", "llama3"))
        
        layout.addRow("API Key:", self.api_key)
        self.api_key.setText(cfg.get("api_key", ""))
        
        layout.addRow("Base URL:", self.base_url)
        self.base_url.setText(cfg.get("base_url", ""))
        
        return widget

    def _create_folder_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.folder_list = QListWidget()
        # 실제 등록된 폴더 목록 불러오기 (예시)
        for path in self.indexer.monitor.watch_list.keys():
            self.folder_list.addItem(path)
            
        layout.addWidget(QLabel("모니터링 중인 폴더:"))
        layout.addWidget(self.folder_list)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("추가")
        add_btn.clicked.connect(self._add_folder)
        del_btn = QPushButton("삭제")
        del_btn.clicked.connect(self._remove_folder)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)
        
        return widget

    def _create_tag_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 검색바
        search_layout = QHBoxLayout()
        self.tag_search_input = QLineEdit()
        self.tag_search_input.setPlaceholderText("태그 검색...")
        self.tag_search_input.textChanged.connect(self._filter_tag_list)
        search_layout.addWidget(QLabel("검색:"))
        search_layout.addWidget(self.tag_search_input)
        layout.addLayout(search_layout)
        
        # 태그 목록
        self.tag_list = QListWidget()
        self.tag_list.setSelectionMode(QListWidget.SingleSelection)
        # Global style has 10px padding which squeezes the content. Override it.
        self.tag_list.setStyleSheet("QListWidget::item { padding: 2px; border-bottom: 1px solid #333333; }")
        
        self._load_tag_list()
        
        layout.addWidget(QLabel("등록된 태그 목록:"))
        layout.addWidget(self.tag_list)
        
        # 버튼
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("추가")
        add_btn.clicked.connect(self._add_tag_ui)
        ren_btn = QPushButton("이름 변경")
        ren_btn.clicked.connect(self._rename_tag_ui)
        color_btn = QPushButton("색상 변경")
        color_btn.clicked.connect(self._change_tag_color_ui)
        del_btn = QPushButton("삭제")
        del_btn.clicked.connect(self._delete_tag_ui)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(ren_btn)
        btn_layout.addWidget(color_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)

        return widget

    def _load_tag_list(self, filter_text=""):
        self.tag_list.clear()
        tags = self.indexer.db.get_all_tags() # (name, color)
        
        for name, color in tags:
            if filter_text and filter_text.lower() not in name.lower():
                continue
                
            item = QListWidgetItem(self.tag_list)
            # 커스텀 위젯 사용하여 태그 칩 느낌 구현
            # 하지만 QListWidget Selection 모델 유지를 위해 Item Delegate나 단순 텍스트+ColorRole 사용 고려.
            # 1-2 요구사항: 1-1과 유사한 서식. 'x' 없어도 됨. 배경색 변경.
            # -> 간단하게 아이콘이나 배경색을 리스트 아이템에 적용?
            # 칩 스타일을 위해 커스텀 위젯 setItemWidget 사용.
            
            item.setSizeHint(QSize(0, 50)) # 높이 넉넉하게 확보
            
            # 컨테이너 위젯 (칩 모양)
            container = QWidget()
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(5, 5, 5, 5) # 여백 조정
            
            chip = QLabel(name)
            chip.setAlignment(Qt.AlignCenter)
            bg_color = QColor(color)
            # Calculate luminance to decide text color
            luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue())
            text_color = "black" if luminance > 128 else "white"

            chip.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: {text_color};
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-weight: bold;
                }}
            """)
            chip.setMinimumWidth(50)
            chip.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            
            h_layout.addWidget(chip)
            h_layout.addStretch() # 왼쪽 정렬
            
            self.tag_list.setItemWidget(item, container)
            
            # Store data in item for retrieval
            item.setData(Qt.UserRole, name)
            item.setData(Qt.UserRole + 1, color) 

    def _filter_tag_list(self, text):
        self._load_tag_list(text)

    def _change_tag_color_ui(self):
        item = self.tag_list.currentItem()
        if not item: return
        
        tag_name = item.data(Qt.UserRole)
        current_color = item.data(Qt.UserRole + 1)
        
        from PySide6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(QColor(current_color), self, "태그 색상 선택")
        
        if color.isValid():
            new_color = color.name()
            if self.indexer.db.update_tag_color(tag_name, new_color):
                self._load_tag_list(self.tag_search_input.text()) # Refresh list with new color

    def _add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "폴더 선택")
        if folder:
            # 중복 체크
            if folder in self.indexer.config.get_folders():
                QMessageBox.warning(self, "경고", "이미 등록된 폴더입니다.")
                return
                
            self.indexer.index_folder(folder)
            self.folder_list.addItem(folder)

    def _remove_folder(self):
        items = self.folder_list.selectedItems()
        if not items:
            QMessageBox.warning(self, "경고", "삭제할 폴더를 선택해주세요.")
            return
        
        for item in items:
            folder = item.text()
            self.indexer.remove_folder(folder)
            self.folder_list.takeItem(self.folder_list.row(item))

    def _add_tag_ui(self):
        from PySide6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "태그 추가", "새 태그 이름:")
        if ok and text:
            existing_tags = [t[0] for t in self.indexer.db.get_all_tags()]
            if text in existing_tags:
                QMessageBox.warning(self, "경고", "이미 존재하는 태그입니다.")
                return
            self.indexer.db.add_tag(text)
            self._load_tag_list(self.tag_search_input.text())

    def _delete_tag_ui(self):
        item = self.tag_list.currentItem()
        if not item:
            QMessageBox.warning(self, "경고", "삭제할 태그를 선택해주세요.")
            return
        
        tag = item.data(Qt.UserRole)
        reply = QMessageBox.question(self, "태그 삭제", f"'{tag}' 태그를 삭제하시겠습니까?\n이 태그가 지정된 파일들에서 태그 정보가 사라집니다.",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.indexer.db.delete_tag(tag)
            self._load_tag_list(self.tag_search_input.text())

    def _rename_tag_ui(self):
        item = self.tag_list.currentItem()
        if not item: return
        
        old_name = item.data(Qt.UserRole)
        from PySide6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, "태그 이름 변경", "새 이름:", text=old_name)
        if ok and new_name and new_name != old_name:
            if self.indexer.db.rename_tag(old_name, new_name):
                self._load_tag_list(self.tag_search_input.text())
            else:
                QMessageBox.warning(self, "오류", "이름 변경 실패 (중복된 이름 등)")

    def accept(self):
        # LLM 설정 저장
        self.indexer.config.set_llm_config(
            self.llm_provider.currentText(),
            self.llm_model.text(),
            self.api_key.text(),
            base_url=self.base_url.text()
        )
        self.indexer.reload_tagger() # Reload tagger with new config
        super().accept()
