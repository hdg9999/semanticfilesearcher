from PySide6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QListWidgetItem, 
                               QLabel, QPushButton, QHBoxLayout, QFrame, QWidget, QSizeGrip)
from PySide6.QtCore import QTimer, Qt, QPoint
from ui.components.spinner import LoadingSpinner
import time

class QueueStatusDialog(QDialog):
    def __init__(self, queue_manager, parent=None):
        super().__init__(parent)
        self.queue_manager = queue_manager
        self.setWindowTitle("Indexing Queue Status")
        self.resize(500, 450)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setStyleSheet("border: 1px solid #444444; background-color: #2b2b2b;")
        
        # Window Dragging State
        self.old_pos = None
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Custom Header
        header = QWidget()
        header.setStyleSheet("background-color: #1e1e1e; border-bottom: 1px solid #333333;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        title = QLabel("대기열") # En: Indexing Queue
        title.setStyleSheet("font-weight: bold; border: none;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        close_btn_header = QPushButton("X")
        close_btn_header.setFixedSize(24, 24)
        close_btn_header.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; font-weight: bold; color: white; }
            QPushButton:hover { color: white; background-color: #c42b1c; }
        """)
        close_btn_header.clicked.connect(self.close)
        header_layout.addWidget(close_btn_header)
        
        layout.addWidget(header)
        
        # Content Container (to add margins for the rest)
        content_widget = QWidget()
        content_widget.setStyleSheet("border: none;")
        content_layout = QVBoxLayout(content_widget)
        
        # Current Processing Section
        current_layout = QHBoxLayout()
        self.spinner = LoadingSpinner(self)
        self.spinner.setVisible(False)
        self.current_label = QLabel("현재 작업 없음") # En: Idle
        self.current_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        
        current_layout.addWidget(self.spinner)
        current_layout.addWidget(self.current_label)
        current_layout.addWidget(self.current_label)
        current_layout.addStretch()
        content_layout.addLayout(current_layout)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setFrameShadow(QFrame.Sunken)
        content_layout.addWidget(line)
        
        self.status_label = QLabel("로딩 중...")
        content_layout.addWidget(self.status_label)
        
        self.list_widget = QListWidget()
        content_layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("새로고침") # En: Refresh
        self.refresh_btn.clicked.connect(self.refresh_list)
        
        self.close_btn = QPushButton("닫기") # En: Close
        self.close_btn.clicked.connect(self.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.close_btn)
        
        # Resizing Grip
        self.size_grip = QSizeGrip(self)
        btn_layout.addWidget(self.size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        
        content_layout.addLayout(btn_layout)
        
        layout.addWidget(content_widget)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_list)
        self.timer.start(500) # Faster refresh for animation responsiveness
        
        self.refresh_list()

    def refresh_list(self):
        # 1. Update Current Task
        current_task = self.queue_manager.get_current_task()
        if current_task:
            self.spinner.setVisible(True)
            self.current_label.setText(f"처리 중: {current_task.path}") # En: Processing: ...
        else:
            self.spinner.setVisible(False)
            self.current_label.setText("현재 작업 없음") # En: Idle

        # 2. Update Pending List
        items = self.queue_manager.get_pending_items()
        self.status_label.setText(f"대기 중인 작업: {len(items)}") # En: Pending Tasks: ...
        
        self.list_widget.clear()
        # Sort by priority (Delete first) then timestamp
        items.sort(key=lambda x: (x.priority, x.timestamp))
        
        for item in items:
            status_text = "DELETE" if item.status == "deleted" else "UPDATE"
            time_ago = int(time.time() - item.timestamp)
            text = f"[{status_text}] {item.path} ({time_ago}s ago)"
            
            list_item = QListWidgetItem(text)
            if item.status == "deleted":
                list_item.setForeground(Qt.red)
            self.list_widget.addItem(list_item)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None
