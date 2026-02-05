from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea
from PySide6.QtCore import Qt
import os
from datetime import datetime

class DetailPane(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(180)
        self.setObjectName("detailPane")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(15)
        
        self.icon_label = QLabel("📄")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setProperty("labelType", "icon")
        layout.addWidget(self.icon_label)
        
        self.name_label = QLabel("파일을 선택하세요")
        self.name_label.setWordWrap(True)
        self.name_label.setProperty("labelType", "fileName")
        layout.addWidget(self.name_label)
        
        layout.addWidget(self._create_section("경로", "path_label"))
        layout.addWidget(self._create_section("수정일", "date_label"))
        layout.addWidget(self._create_section("태그", "tags_label"))
        
        layout.addStretch()

    def _create_section(self, title, attr_name):
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(5)
        
        title_lbl = QLabel(title)
        title_lbl.setProperty("labelType", "sectionTitle")
        
        val_lbl = QLabel("-")
        val_lbl.setWordWrap(True)
        val_lbl.setProperty("labelType", "sectionValue")
        
        setattr(self, attr_name, val_lbl)
        vbox.addWidget(title_lbl)
        vbox.addWidget(val_lbl)
        return container

    def update_info(self, file_path, tags=None, icon=None):
        self.name_label.setText(os.path.basename(file_path))
        self.path_label.setText(file_path)
        
        if icon:
            self.icon_label.setPixmap(icon.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.icon_label.setText("📄") # Fallback text icon
        
        mtime = os.path.getmtime(file_path)
        dt = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        self.date_label.setText(dt)
        
        if tags:
            self.tags_label.setText(", ".join(tags))
        else:
            self.tags_label.setText("태그 없음")
