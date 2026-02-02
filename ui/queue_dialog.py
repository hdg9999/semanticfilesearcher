from PySide6.QtWidgets import (QDialog, QVBoxLayout, QListWidget, QListWidgetItem, 
                               QLabel, QPushButton, QHBoxLayout, QFrame)
from PySide6.QtCore import QTimer, Qt
from ui.components.spinner import LoadingSpinner
import time

class QueueStatusDialog(QDialog):
    def __init__(self, queue_manager, parent=None):
        super().__init__(parent)
        self.queue_manager = queue_manager
        self.setWindowTitle("Indexing Queue Status")
        self.resize(500, 450)
        
        layout = QVBoxLayout(self)
        
        # Current Processing Section
        current_layout = QHBoxLayout()
        self.spinner = LoadingSpinner(self)
        self.spinner.setVisible(False)
        self.current_label = QLabel("Idle")
        self.current_label.setStyleSheet("font-weight: bold; color: #4CAF50;")
        
        current_layout.addWidget(self.spinner)
        current_layout.addWidget(self.current_label)
        current_layout.addStretch()
        layout.addLayout(current_layout)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        self.status_label = QLabel("Loading...")
        layout.addWidget(self.status_label)
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_list)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_list)
        self.timer.start(500) # Faster refresh for animation responsiveness
        
        self.refresh_list()

    def refresh_list(self):
        # 1. Update Current Task
        current_task = self.queue_manager.get_current_task()
        if current_task:
            self.spinner.setVisible(True)
            self.current_label.setText(f"Processing: {current_task.path}")
        else:
            self.spinner.setVisible(False)
            self.current_label.setText("Idle")

        # 2. Update Pending List
        items = self.queue_manager.get_pending_items()
        self.status_label.setText(f"Pending Tasks: {len(items)}")
        
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
