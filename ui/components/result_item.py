import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMenu)
from PySide6.QtCore import Qt, Signal, QSize, QUrl
from PySide6.QtGui import QIcon, QAction, QDesktopServices

class FileResultWidget(QFrame):
    clicked = Signal(str) # 파일 경로 전달
    double_clicked = Signal(str)
    manage_tags_requested = Signal(str)
    
    def __init__(self, file_path, view_mode="list", parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.view_mode = view_mode
        self.file_name = os.path.basename(file_path)
        
        self.setMouseTracking(True)
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("fileResult")
        if self.view_mode == "list":
            layout = QHBoxLayout(self)
        else:
            layout = QVBoxLayout(self)
        
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 파일 아이콘 (시스템 아이콘 사용)
        from PySide6.QtWidgets import QFileIconProvider
        from PySide6.QtCore import QFileInfo
        
        provider = QFileIconProvider()
        icon = provider.icon(QFileInfo(self.file_path))
        
        self.icon_label = QLabel()
        self.icon_label.setPixmap(icon.pixmap(QSize(32, 32)))
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        
        # 정보 영역
        info_layout = QVBoxLayout()
        self.name_label = QLabel(self.file_name)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        if self.view_mode == "list":
            info_layout.addWidget(self.name_label)
            self.path_label = QLabel(self.file_path)
            self.path_label.setStyleSheet("color: #888888; font-size: 11px;")
            info_layout.addWidget(self.path_label)
            layout.addLayout(info_layout, stretch=1)
        else:
            # 아이콘 모드 설정
            self.setFixedSize(120, 140)
            self.name_label.setAlignment(Qt.AlignCenter)
            self.name_label.setWordWrap(True) # 긴 파일명 줄바꿈
            self.name_label.setStyleSheet("font-size: 12px;") # 폰트 크기 조정
            info_layout.addWidget(self.name_label)
            layout.addLayout(info_layout)
            
        # 호버 버튼 (기본 숨김)
        self.actions_widget = QWidget()
        actions_layout = QHBoxLayout(self.actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        self.open_folder_btn = QPushButton("📂")
        self.open_folder_btn.setToolTip("폴더 열기")
        self.open_folder_btn.clicked.connect(self.open_folder)
        
        self.more_btn = QPushButton("⋮")
        self.more_btn.setToolTip("추가 메뉴")
        self.more_btn.clicked.connect(self.show_context_menu)
        
        actions_layout.addWidget(self.open_folder_btn)
        actions_layout.addWidget(self.more_btn)
        self.actions_widget.setVisible(False)
        layout.addWidget(self.actions_widget, alignment=Qt.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.file_path)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self.file_path)

    def enterEvent(self, event):
        self.actions_widget.setVisible(True)
        self.setStyleSheet("#fileResult { background-color: #37373d; border-radius: 4px; }")

    def leaveEvent(self, event):
        self.actions_widget.setVisible(False)
        self.setStyleSheet("#fileResult { background-color: transparent; }")

    def open_folder(self):
        folder = os.path.dirname(self.file_path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def show_context_menu(self):
        menu = QMenu(self)
        info_act = QAction("파일 정보 보기", self)
        tag_act = QAction("태그 관리", self)
        tag_act.triggered.connect(lambda: self.manage_tags_requested.emit(self.file_path))
        del_act = QAction("파일 삭제", self)
        
        menu.addAction(info_act)
        menu.addAction(tag_act)
        menu.addSeparator()
        menu.addAction(del_act)
        
        menu.exec(self.more_btn.mapToGlobal(self.more_btn.rect().bottomLeft()))
