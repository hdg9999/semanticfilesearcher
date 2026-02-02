from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
                             QWidget, QLabel, QLineEdit, QPushButton, QComboBox, 
                             QFormLayout, QListWidget, QListWidgetItem, QMessageBox, QFileDialog)
from PySide6.QtCore import Qt

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
        
        cfg = self.indexer.config.get_llm_config()
        
        layout.addRow("LLM 제공자:", self.llm_provider)
        self.llm_provider.setCurrentText(cfg.get("provider", "Ollama"))
        
        layout.addRow("모델명:", self.llm_model)
        self.llm_model.setText(cfg.get("model", "llama3"))
        
        layout.addRow("API Key:", self.api_key)
        self.api_key.setText(cfg.get("api_key", ""))
        
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
        
        self.tag_list = QListWidget()
        tags = self.indexer.db.get_all_tags()
        self.tag_list.addItems(tags)
        
        layout.addWidget(QLabel("등록된 태그 목록:"))
        layout.addWidget(self.tag_list)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("추가")
        add_btn.clicked.connect(self._add_tag_ui)
        ren_btn = QPushButton("이름 변경")
        ren_btn.clicked.connect(self._rename_tag_ui)
        del_btn = QPushButton("삭제")
        del_btn.clicked.connect(self._delete_tag_ui)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(ren_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)

        return widget

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
            if text in self.indexer.db.get_all_tags():
                QMessageBox.warning(self, "경고", "이미 존재하는 태그입니다.")
                return
            self.indexer.db.add_tag(text)
            self.tag_list.addItem(text)

    def _delete_tag_ui(self):
        item = self.tag_list.currentItem()
        if not item:
            QMessageBox.warning(self, "경고", "삭제할 태그를 선택해주세요.")
            return
        
        tag = item.text()
        reply = QMessageBox.question(self, "태그 삭제", f"'{tag}' 태그를 삭제하시겠습니까?\n이 태그가 지정된 파일들에서 태그 정보가 사라집니다.",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.indexer.db.delete_tag(tag)
            self.tag_list.takeItem(self.tag_list.row(item))

    def _rename_tag_ui(self):
        item = self.tag_list.currentItem()
        if not item: return
        
        old_name = item.text()
        from PySide6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, "태그 이름 변경", "새 이름:", text=old_name)
        if ok and new_name and new_name != old_name:
            if self.indexer.db.rename_tag(old_name, new_name):
                item.setText(new_name)
            else:
                QMessageBox.warning(self, "오류", "이름 변경 실패 (중복된 이름 등)")

    def accept(self):
        # LLM 설정 저장
        self.indexer.config.set_llm_config(
            self.llm_provider.currentText(),
            self.llm_model.text(),
            self.api_key.text()
        )
        self.indexer.reload_tagger() # Reload tagger with new config
        super().accept()
