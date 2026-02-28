from PySide6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLineEdit, 
                               QStackedWidget, QLabel, QFrame)
from PySide6.QtCore import Qt, Signal, QSize, QEvent
from PySide6.QtGui import QIcon, QAction

import os

class PathBar(QWidget):
    path_changed = Signal(str)
    refresh_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_path = ""
        self.setObjectName("pathBar")
        self._setup_ui()
        
        # Load Styles
        # Styles are now handled by StyleManager loading dark.qss/light.qss
        # self.setStyleSheet(...) -> REMOVED

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)

        # Wrapper for Breadcrumb/Edit
        self.stack = QStackedWidget()
        
        # 1. Breadcrumb View
        self.breadcrumb_container = QWidget()
        self.breadcrumb_layout = QHBoxLayout(self.breadcrumb_container)
        self.breadcrumb_layout.setContentsMargins(0, 0, 0, 0)
        self.breadcrumb_layout.setSpacing(0)
        self.breadcrumb_layout.setAlignment(Qt.AlignLeft)
        
        # Fill empty space in breadcrumb to detect click
        self.breadcrumb_bg = ClickableWidget()
        self.breadcrumb_bg.clicked.connect(self.switch_to_edit_mode)
        self.breadcrumb_layout.addWidget(self.breadcrumb_bg, 1) # Stretch

        self.stack.addWidget(self.breadcrumb_container)

        # 2. Edit View
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("경로 입력...")
        self.path_edit.returnPressed.connect(self.on_path_entered)
        # Focus out event handling could be done by event filter or subclass
        self.path_edit.installEventFilter(self)

        self.stack.addWidget(self.path_edit)

        layout.addWidget(self.stack, 1)

        # Refresh Button
        self.refresh_btn = QPushButton()
        self.refresh_btn.setObjectName("refreshBtn")
        # Initial icon load
        self.update_icons("_white") # Default to dark theme icon
        self.refresh_btn.setFixedSize(28, 28)
        self.refresh_btn.setToolTip("새로고침")
        self.refresh_btn.clicked.connect(self.refresh_clicked.emit)
        
        layout.addWidget(self.refresh_btn)

    def update_icons(self, suffix):
        """Updates icons based on theme."""
        from ui.style_manager import StyleManager
        icon_path = StyleManager().get_resource_path(f"resources/icons/refresh{suffix}.svg")
        if os.path.exists(icon_path):
            self.refresh_btn.setIcon(QIcon(icon_path))
        else:
            print(f"Icon not found: {icon_path}")

    def set_path(self, path):
        self.current_path = os.path.normpath(path)
        self.path_edit.setText(self.current_path)
        self.rebuild_breadcrumbs()
        self.stack.setCurrentIndex(0) # Show breadcrumbs

    def rebuild_breadcrumbs(self):
        # Clear existing items (except the stretcher at the end)
        while self.breadcrumb_layout.count() > 1:
            item = self.breadcrumb_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Split path
        parts = self.current_path.split(os.sep)
        # Handle dry run or empty
        if not self.current_path:
            return

        accumulated_path = ""
        for i, part in enumerate(parts):
            if i == 0 and part.endswith(':'): # Drive letter on Windows
                 accumulated_path = part + os.sep
            else:
                 accumulated_path = os.path.join(accumulated_path, part)
            
            # Button for part
            btn = QPushButton(part if part else os.sep) # Root might be empty string in split
            if not part and i==0: btn.setText(os.sep) # Handle linux root if needed, but windows 'C:' 

            btn.setObjectName("breadcrumbBtn")
            # Store path in property or use closure? Closure is easier but verify loop variable capture
            # Using partial or default arg to capture value
            btn.clicked.connect(lambda checked=False, p=accumulated_path: self.path_changed.emit(p))
            
            self.breadcrumb_layout.insertWidget(self.breadcrumb_layout.count()-1, btn)
            
            # Separator
            if i < len(parts) - 1:
                sep = QLabel(" > ")
                sep.setStyleSheet("color: #888; margin: 0 2px;")
                self.breadcrumb_layout.insertWidget(self.breadcrumb_layout.count()-1, sep)

    def switch_to_edit_mode(self):
        self.stack.setCurrentIndex(1)
        self.path_edit.setFocus()
        self.path_edit.selectAll()

    def on_path_entered(self):
        new_path = self.path_edit.text()
        if os.path.exists(new_path) and os.path.isdir(new_path):
            self.path_changed.emit(new_path)
            self.set_path(new_path) # Switch back to breadcrumb
        else:
            # Shake or error feedback?
            self.path_edit.setStyleSheet("border: 1px solid red;")

    def eventFilter(self, obj, event):
        if obj == self.path_edit and event.type() == QEvent.FocusOut:
            self.set_path(self.current_path) # Revert and switch back
            return True
        return super().eventFilter(obj, event)    

class ClickableWidget(QWidget):
    clicked = Signal()
    def mousePressEvent(self, event):
        self.clicked.emit()
