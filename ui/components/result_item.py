import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMenu)
from PySide6.QtCore import Qt, Signal, QSize, QUrl
from PySide6.QtGui import QIcon, QAction, QDesktopServices

class FileResultWidget(QFrame):
    clicked = Signal(str) # 파일 경로 전달
    double_clicked = Signal(str)
    tag_clicked = Signal(str) # 태그 클릭 시 시그널
    manage_tags_requested = Signal(str)

    def __init__(self, file_path, view_mode="list", tags=None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.view_mode = view_mode
        self.tags = tags or []
        self.file_name = os.path.basename(file_path)
        
        self.setMouseTracking(True)
        self._setup_ui()
        
        # Load style
        from ui.style_manager import StyleManager
        style = StyleManager().get_component_style("result_item")
        if style:
            self.setStyleSheet(style)

    def _setup_ui(self):
        self.setObjectName("fileResult")
        if self.view_mode == "list":
            self.setFixedHeight(60)
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
        if self.view_mode == "list":
            # 3-Column Layout: Icon | Info (Name+Path) | Tags
            
            # 2. Info Column (Name + Path)
            info_column = QWidget()
            info_layout = QVBoxLayout(info_column)
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(5) # Spacing between Name and Path
            
            self.name_label.setObjectName("fileNameLabel")
            info_layout.addWidget(self.name_label)
            
            self.path_label = QLabel(self.file_path)
            self.path_label.setObjectName("filePathLabel")
            info_layout.addWidget(self.path_label)
            
            info_layout.setAlignment(Qt.AlignVCenter)
            layout.addWidget(info_column, stretch=1)
            
            # 3. Tags Column
            if self.tags:
                tag_column = QWidget()
                tag_vbox = QVBoxLayout(tag_column)
                tag_vbox.setContentsMargins(10, 0, 0, 0) # Left margin to separate from info
                tag_vbox.setSpacing(5) # Should calculate to align with info_layout spacing if needed
                
                # Row 1 (Aligns with Name)
                row1_widget = QWidget()
                row1_layout = QHBoxLayout(row1_widget)
                row1_layout.setContentsMargins(0, 0, 0, 0)
                row1_layout.setSpacing(5)
                row1_layout.setAlignment(Qt.AlignLeft)
                
                # Row 2 (Aligns with Path)
                row2_widget = QWidget()
                row2_layout = QHBoxLayout(row2_widget)
                row2_layout.setContentsMargins(0, 0, 0, 0)
                row2_layout.setSpacing(5)
                row2_layout.setAlignment(Qt.AlignLeft)
                
                display_tags = self.tags[:6]
                
                for i, (name, color) in enumerate(display_tags):
                    chip = self._create_tag_chip(name, color)
                    if i < 3:
                        row1_layout.addWidget(chip)
                    else:
                        row2_layout.addWidget(chip)
                
                # Add '...' if needed
                if len(self.tags) > 6:
                    more_lbl = QLabel("...")
                    more_lbl.setStyleSheet("color: #888;")
                    row2_layout.addWidget(more_lbl)
                
                # We need to ensure row heights match Info column items for "Grid-like" feel
                # Name Label height is determined by font. Tag chip height is fixed 20.
                # Just adding them to VBox might not align perfectly if Name Label is tall.
                # However, with standard fonts, it should be close.
                
                tag_vbox.addWidget(row1_widget)
                
                if len(display_tags) > 3:
                    tag_vbox.addWidget(row2_widget)
                else:
                    # Placeholder to maintain spacing if we wanted strict grid, 
                    # but here we just want the first row to align.
                    # If we only have 1 row of tags, it should just align with Name.
                    pass

                tag_vbox.setAlignment(Qt.AlignVCenter)
                layout.addWidget(tag_column)

        else:
            # 아이콘 모드 설정
            self.setFixedSize(120, 140)
            self.name_label.setAlignment(Qt.AlignCenter)
            self.name_label.setWordWrap(True) # 긴 파일명 줄바꿈
            # Style handled by QSS via ObjectName
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

    def _create_tag_chip(self, name, color):
        lbl = QPushButton(name) # Clickable like a button
        lbl.setCursor(Qt.PointingHandCursor)
        # Determine text color based on brightness
        # Simple brightness formula
        c = color.lstrip('#')
        rgb = tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
        brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
        text_color = "black" if brightness > 128 else "white"

        lbl.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border-radius: 10px;
                padding: 2px 8px;
                border: none;
                font-size: 11px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)
        lbl.setFixedHeight(20)
        lbl.clicked.connect(lambda: self.tag_clicked.emit(name))
        return lbl

    def set_selected(self, selected):
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)
        
        if selected:
            self.actions_widget.setVisible(True)
        else:
            self.actions_widget.setVisible(False)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.file_path)
            # Selection logic will be handled by MainWindow

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.double_clicked.emit(self.file_path)

    def contextMenuEvent(self, event):
        self.show_context_menu()

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
        
        # Show menu at cursor position if triggered by context menu event, or below button
        if self.sender() == self.more_btn:
            menu.exec(self.more_btn.mapToGlobal(self.more_btn.rect().bottomLeft()))
        else:
            menu.exec(self.cursor().pos())

    def set_unregistered_status(self):
        """Displays 'Unregistered' label instead of tags"""
        label = QLabel("미등록 파일")
        label.setStyleSheet("""
            background-color: #555;
            color: #ccc;
            border-radius: 10px;
            padding: 2px 8px;
            font-size: 11px;
            font-weight: bold;
        """)
        label.setFixedSize(80, 24)
        label.setAlignment(Qt.AlignCenter)
        
        if self.view_mode == "list":
             layout = self.layout()
             # We want to put it where tags go.
             # If tags are empty, the 3rd column (tag_column) might not exist.
             # So layout has Icon Label, Info Column.
             
             layout.addWidget(label)
             layout.setAlignment(label, Qt.AlignRight | Qt.AlignVCenter)
        else:
             # Icon mode: Add below name
             self.layout().addWidget(label, alignment=Qt.AlignCenter)

