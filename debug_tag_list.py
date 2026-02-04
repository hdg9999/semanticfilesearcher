import sys
from PySide6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QListWidget, 
                               QListWidgetItem, QWidget, QHBoxLayout, QLabel, QSizePolicy)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor

class DebugTagDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tag List Debugger")
        self.resize(400, 600)
        self.layout = QVBoxLayout(self)
        
        self.tag_list = QListWidget()
        self.layout.addWidget(self.tag_list)
        
        # Test Data: Various lengths and colors
        self.dummy_tags = [
            ("short", "#FF0000"),
            ("medium_tag", "#00FF00"),
            ("very_long_tag_name_example", "#0000FF"),
            ("korean_tag_테스트", "#FFFF00"),
            ("long_korean_tag_긴이름태그테스트입니다", "#00FFFF"),
            ("mixed_tag_123_abc", "#FF00FF"),
        ]
        
        self.load_tags()

    def load_tags(self):
        self.tag_list.clear()
        
        for name, color in self.dummy_tags:
            item = QListWidgetItem(self.tag_list)
            
            # --- Current Implementation Logic (Simulated) ---
            # Trying to reproduce the issue
            
            item.setSizeHint(QSize(0, 50)) # Height increased for safety
            
            container = QWidget()
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(5, 5, 5, 5)
            
            chip = QLabel(name)
            chip.setAlignment(Qt.AlignCenter)
            
            bg_color = QColor(color)
            luminance = (0.299 * bg_color.red() + 0.587 * bg_color.green() + 0.114 * bg_color.blue())
            text_color = "black" if luminance > 128 else "white"

            # Style from SettingsDialog
            chip.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: {text_color};
                    border-radius: 12px;
                    padding: 4px 10px;
                    font-weight: bold;
                }}
            """)
            
            # Using the latest attempted fix settings
            chip.setMinimumWidth(50) 
            chip.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed) 
            # chip.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed) # Previous attempt
            
            h_layout.addWidget(chip)
            h_layout.addStretch() 
            
            self.tag_list.setItemWidget(item, container)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dlg = DebugTagDialog()
    dlg.show()
    sys.exit(app.exec())
