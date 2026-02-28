from PySide6.QtWidgets import (QWidget, QLineEdit, QLabel, QHBoxLayout, 
                             QPushButton, QFrame, QCompleter, QApplication, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QSize, QStringListModel
from PySide6.QtGui import QIcon, QPainter, QColor, QBrush, QPen
from ui.components.flow_layout import FlowLayout

class TagLabel(QFrame):
    removed = Signal(str)

    def __init__(self, text, color="#007acc", parent=None):
        super().__init__(parent)
        self.text = text
        self.color = color
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 4, 2)
        layout.setSpacing(4)
        
        self.label = QLabel(text)
        self.label.setStyleSheet("color: white; font-weight: bold; background-color: transparent; border: none; text-decoration: none;")
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(16, 16)
        self.close_btn.setFlat(True)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton { 
                color: white; 
                border: none; 
                font-weight: bold; 
                margin-top: -2px; 
                background-color: transparent; 
                padding: 0px; /* Reset padding to prevent clipping */
                font-size: 14px; /* Ensure visible size */
            }
            QPushButton:hover { color: #ffcccc; background-color: transparent; }
        """)
        self.close_btn.clicked.connect(lambda: self.removed.emit(self.text))
        
        layout.addWidget(self.label)
        layout.addWidget(self.close_btn)
        
        self.setStyleSheet(f"""
            TagLabel {{
                background-color: {color};
                border-radius: 14px; /* Increased radius */
                border: none; /* Ensure no border from QFrame */
            }}
        """)
        self.setFixedHeight(28)

    def update_color(self, color):
        self.color = color
        bg_color = QColor(color)
        luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue())
        text_color = "black" if luminance > 128 else "white"
        
        # Update close button color for visibility
        close_color = "black" if luminance > 128 else "white"
        hover_color = "#333333" if luminance > 128 else "#ffcccc"

        self.label.setStyleSheet(f"color: {text_color}; font-weight: bold; background-color: transparent; border: none; text-decoration: none;")
        self.close_btn.setStyleSheet(f"""
            QPushButton {{ 
                color: {close_color}; 
                border: none; 
                font-weight: bold; 
                margin-top: -2px; 
                background-color: transparent;
                padding: 0px;
                font-size: 14px;
            }}
            QPushButton:hover {{ color: {hover_color}; background-color: transparent; }}
        """)

        self.setStyleSheet(f"""
            TagLabel {{
                background-color: {color};
                border-radius: 14px;
                border: none; /* Ensure no border from QFrame */
            }}
        """)

class CheckableTagChip(QFrame):
    toggled = Signal(bool)

    def __init__(self, text, color="#007acc", checked=False, parent=None):
        super().__init__(parent)
        self.text = text
        self.base_color = color
        self.is_checked = checked
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(0)
        
        self.label = QLabel(text)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        self.setCursor(Qt.PointingHandCursor)
        self.update_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_checked = not self.is_checked
            self.update_style()
            self.toggled.emit(self.is_checked)
        super().mousePressEvent(event)

    def set_checked(self, checked):
        if self.is_checked != checked:
            self.is_checked = checked
            self.update_style()
            self.toggled.emit(self.is_checked)

    def update_style(self):
        # Determine text color based on background luminance for better contrast
        if self.is_checked:
            bg_color = QColor(self.base_color)
            luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue())
            text_color = "black" if luminance > 128 else "white"
            
            self.setStyleSheet(f"""
                CheckableTagChip {{
                    background-color: {self.base_color};
                    border: 1px solid {self.base_color};
                    border-radius: 14px;
                }}
            """)
            self.label.setStyleSheet(f"color: {text_color}; font-weight: bold; background-color: transparent; border: none;")
        else:
            # Unchecked: transparent background, colored border and text
            self.setStyleSheet(f"""
                CheckableTagChip {{
                    background-color: transparent;
                    border: 1px solid {self.base_color};
                    border-radius: 14px;
                }}
            """)
            self.label.setStyleSheet(f"color: {self.base_color}; font-weight: bold; background-color: transparent; border: none;")

class TagInputWidget(QFrame):
    tags_changed = Signal(list)
    return_pressed = Signal() # Enter key pressed in input

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tags = []
        
        self.tags = []
        
        # Load style
        from ui.style_manager import StyleManager
        style = StyleManager().get_component_style("tag_input")
        if style:
            self.setStyleSheet(style)
        
        self.flow_layout = FlowLayout(self, margin=4, spacing=4)
        
        self.input_edit = QLineEdit(self)
        self.input_edit.setPlaceholderText("태그 입력...")
        self.input_edit.setMinimumWidth(100) # Ensure it has some width
        self.input_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # Styles for QLineEdit are in tag_input.qss
        self.input_edit.returnPressed.connect(self.handle_return)
        self.input_edit.textChanged.connect(self.handle_text_changed)
        # Install event filter to capture backspace
        self.input_edit.installEventFilter(self)
        
        from PySide6.QtWidgets import QWidgetItem
        self.flow_layout.addItem(QWidgetItem(self.input_edit))
        
        self.completer = None
        self.tag_colors = {}

    def set_tag_colors(self, colors):
        self.tag_colors = colors
        # Update existing tags
        for i in range(self.flow_layout.count()):
            item = self.flow_layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, TagLabel):
                if widget.text in colors:
                    widget.update_color(colors[widget.text])

    def set_completer_items(self, items):
        self.completer = QCompleter(items)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        
        # Style the popup
        popup = self.completer.popup()
        popup.setObjectName("tagCompleterPopup")
        
        from ui.style_manager import StyleManager
        style = StyleManager().get_component_style("tag_input")
        if style:
            popup.setStyleSheet(style)
        
        self.input_edit.setCompleter(self.completer)
        # Handle selection from completer
        self.completer.activated.connect(self.add_tag)

    def eventFilter(self, obj, event):
        from PySide6.QtCore import QEvent
        if obj == self.input_edit and event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Backspace and not self.input_edit.text():
                if self.tags:
                    self.remove_tag(self.tags[-1])
                    return True
        return super().eventFilter(obj, event)

    def handle_return(self):
        text = self.input_edit.text().strip()
        if text:
            self.add_tag(text)
        else:
            self.return_pressed.emit()

    def handle_text_changed(self, text):
        pass

    def add_tag(self, text):
        text = text.strip()
        if not text: return
        if text in self.tags: 
            self.input_edit.clear()
            return
            
        self.tags.append(text)
        
        # Determine color
        color = self.tag_colors.get(text, "#007acc")
        
        tag_widget = TagLabel(text, color=color, parent=self)
        # Ensure text color is correct based on background
        tag_widget.update_color(color) 
        
        tag_widget.removed.connect(self.remove_tag)
        tag_widget.show()
        
        from PySide6.QtWidgets import QWidgetItem
        # Remove input from layout, add tag, add input back
        self.flow_layout.removeWidget(self.input_edit)
        self.flow_layout.addItem(QWidgetItem(tag_widget))
        self.flow_layout.addItem(QWidgetItem(self.input_edit))
        
        self.input_edit.setFocus()
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self.input_edit.clear)
        
        self.tags_changed.emit(self.tags)

    def remove_tag(self, text):
        if text in self.tags:
            self.tags.remove(text)
            
            # Find and remove widget
            for i in range(self.flow_layout.count()):
                item = self.flow_layout.itemAt(i)
                widget = item.widget()
                if isinstance(widget, TagLabel) and widget.text == text:
                    widget.hide()
                    self.flow_layout.takeAt(i) 
                    widget.deleteLater()
                    break
            
            self.tags_changed.emit(self.tags)

    def get_tags(self):
        return self.tags

    def clear(self):
        # Remove all tags
        for t in list(self.tags):
            self.remove_tag(t)
