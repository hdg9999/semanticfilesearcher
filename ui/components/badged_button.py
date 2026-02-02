from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QFont, QPen, QBrush

class BadgedButton(QPushButton):
    def __init__(self, icon, parent=None):
        super().__init__(parent)
        self.setIcon(icon)
        self.badge_count = 0
        
        # Style for icon-only button
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #3e3e42;
            }
            QPushButton:pressed {
                background-color: #007acc;
            }
        """)

    def set_badge_count(self, count):
        self.badge_count = count
        self.update() # Trigger repaint

    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self.badge_count > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Badge dimensions
            badge_size = 16
            rect = self.rect()
            
            # Position: Top-right corner
            x = rect.width() - badge_size
            y = 0
            
            badge_rect = QRect(x, y, badge_size, badge_size)
            
            # Draw Badge Background
            painter.setBrush(QBrush(QColor("#FF4081"))) # Pink/Red color
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(badge_rect)
            
            # Draw Badge Text
            painter.setPen(QPen(Qt.white))
            font = painter.font()
            font.setPixelSize(10)
            font.setBold(True)
            painter.setFont(font)
            
            text = str(self.badge_count)
            if self.badge_count > 99:
                text = "99+"
                
            painter.drawText(badge_rect, Qt.AlignCenter, text)
