from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QScrollArea, QWidget, QLabel, QLineEdit, QMessageBox)
from PySide6.QtCore import Qt
from ui.components.tag_input import CheckableTagChip
from ui.components.flow_layout import FlowLayout

class TagSelectionDialog(QDialog):
    def __init__(self, indexer, file_path, parent=None):
        super().__init__(parent)
        self.indexer = indexer
        self.file_path = file_path
        self.setWindowTitle("태그 관리")
        self.resize(450, 550) # Slightly larger for better chip layout
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        
        # 안내 문구 및 파일명
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        file_label = QLabel(f"파일: {file_path}")
        file_label.setStyleSheet("font-weight: bold; color: #666;")
        file_label.setWordWrap(True)
        header_layout.addWidget(file_label)
        header_layout.addWidget(QLabel("적용할 태그를 선택하세요:"))
        self.layout.addLayout(header_layout)
        
        # 필터 입력창
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("태그 검색...")
        self.filter_input.textChanged.connect(self._filter_tags)
        self.layout.addWidget(self.filter_input)
        
        # 태그 영역 (ScrollArea + FlowLayout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        self.tag_container = QWidget()
        self.tag_layout = FlowLayout(self.tag_container, margin=0, spacing=6)
        self.scroll_area.setWidget(self.tag_container)
        
        self.layout.addWidget(self.scroll_area)
        
        self.chips = {} # tag_name: CheckableTagChip
        self._load_tags()
        
        # 새 태그 추가
        add_layout = QHBoxLayout()
        self.new_tag_input = QLineEdit()
        self.new_tag_input.setPlaceholderText("새 태그 이름...")
        add_btn = QPushButton("추가")
        add_btn.clicked.connect(self._add_new_tag)
        add_layout.addWidget(self.new_tag_input)
        add_layout.addWidget(add_btn)
        self.layout.addLayout(add_layout)

        # 하단 버튼
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("저장")
        save_btn.clicked.connect(self._save_tags)
        cancel_btn = QPushButton("취소")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        self.layout.addLayout(btn_layout)

    def _load_tags(self):
        # Clear existing items
        while self.tag_layout.count():
            item = self.tag_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.chips = {}
        
        all_tags = self.indexer.db.get_all_tags()
        file_tags = self.indexer.db.get_tags_for_file(self.file_path)
        
        for tag_tuple in all_tags:
            tag_name = tag_tuple[0]
            tag_color = tag_tuple[1]
            
            is_checked = tag_name in file_tags
            chip = CheckableTagChip(tag_name, color=tag_color, checked=is_checked)
            
            self.tag_layout.addWidget(chip)
            self.chips[tag_name] = chip

    def _filter_tags(self, text):
        text = text.strip().lower()
        for tag_name, chip in self.chips.items():
            if text in tag_name.lower():
                chip.show()
            else:
                chip.hide()

    def _add_new_tag(self):
        tag = self.new_tag_input.text().strip()
        if not tag: return
        
        if tag in self.chips:
            QMessageBox.warning(self, "경고", "이미 존재하는 태그입니다.")
            return

        # 새 태그 DB에 추가
        self.indexer.db.add_tag(tag)
        
        # UI 업데이트 (전체 리로드 대신 최적화 가능하지만, 색상 등 일관성을 위해 리로드)
        self.new_tag_input.clear()
        self.filter_input.clear() # 필터 초기화하여 새 태그 보이게 함
        self._load_tags()
        
        # 방금 추가한 태그 자동 선택
        if tag in self.chips:
            self.chips[tag].set_checked(True)
            # 스크롤을 맨 아래로? FlowLayout이라 위치 보장 어려움.

    def _save_tags(self):
        selected_tags = []
        for tag_name, chip in self.chips.items():
            if chip.is_checked:
                selected_tags.append(tag_name)
        
        self.indexer.db.update_file_tags(self.file_path, selected_tags)
        self.accept()
