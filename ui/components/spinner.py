from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen

class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._timer.start(50)  # 50ms interval
        self._color = QColor(Qt.white)

    def _rotate(self):
        self._angle = (self._angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        mx = self.width() / 2
        my = self.height() / 2
        radius = min(mx, my) * 0.8
        
        painter.translate(mx, my)
        painter.rotate(self._angle)
        
        # Draw spinner lines
        lines = 12
        for i in range(lines):
            painter.rotate(360 / lines)
            alpha = int(255 * (i / lines))
            color = QColor(self._color)
            color.setAlpha(alpha)
            
            pen = QPen(color)
            pen.setWidth(2)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            
            painter.drawLine(0, int(radius * 0.5), 0, int(radius))
