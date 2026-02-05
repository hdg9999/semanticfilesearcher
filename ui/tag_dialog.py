from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QListWidgetItem, QCheckBox, QLabel, 
                             QLineEdit, QMessageBox)
from PySide6.QtCore import Qt

class TagSelectionDialog(QDialog):
    def __init__(self, indexer, file_path, parent=None):
        super().__init__(parent)
        self.indexer = indexer
        self.file_path = file_path
        self.setWindowTitle("태그 관리")
        self.resize(400, 500)
        
        self.layout = QVBoxLayout(self)
        
        # 안내 문구
        self.layout.addWidget(QLabel(f"파일: {file_path}"))
        self.layout.addWidget(QLabel("적용할 태그를 선택하세요:"))
        
        # 태그 목록
        self.tag_list = QListWidget()
        self.items = {} # tag_name: item mapping
        self._load_tags()
        self.layout.addWidget(self.tag_list)
        
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
        all_tags = self.indexer.db.get_all_tags()
        file_tags = self.indexer.db.get_tags_for_file(self.file_path)
        
        self.tag_list.clear()
        self.items = {}
        
        for tag_tuple in all_tags:
            tag_name = tag_tuple[0]
            tag_color = tag_tuple[1]
            
            item = QListWidgetItem(tag_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            
            check_state = Qt.Checked if tag_name in file_tags else Qt.Unchecked
            item.setCheckState(check_state)
            item.setData(Qt.UserRole, tag_color) # Store color for potential use
            
            self.tag_list.addItem(item)
            self.items[tag_name] = item

    def _add_new_tag(self):
        tag = self.new_tag_input.text().strip()
        if not tag: return
        
        if tag in self.items:
            QMessageBox.warning(self, "경고", "이미 존재하는 태그입니다.")
            return

        # DB에 추가는 저장 시점에 하는게 깔끔하지만, 
        # 여기서는 즉시 목록에 반영해야 하므로 미리 DB에 추가하지 않고 UI 리스트에만 추가할 수도 있음.
        # 하지만 일관성을 위해 DB에 바로 추가하고 리로드하겠습니다.
        # 혹은 UI에만 추가했다가 저장을 누르면 한꺼번에 처리하는게 롤백 관점에서 좋음.
        # 기존 로직과 단순함을 위해 DB 즉시 추가를 방지하고 UI 아이템으로 추가함.
        # 하지만 다른 파일에서도 써야하므로, 새 태그는 '전역 태그'로 간주하고 DB에 추가하는 것이 일반적임.
        
        self.indexer.db.add_tag(tag)
        self.new_tag_input.clear()
        self._load_tags() # 리로드
        
        # 방금 추가한 태그는 체크 상태로
        if tag in self.items:
            self.items[tag].setCheckState(Qt.Checked)

    def _save_tags(self):
        selected_tags = []
        for i in range(self.tag_list.count()):
            item = self.tag_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_tags.append(item.text())
        
        self.indexer.db.update_file_tags(self.file_path, selected_tags)
        self.accept()
