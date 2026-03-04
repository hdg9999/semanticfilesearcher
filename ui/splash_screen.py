import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QPixmap, QFont, QPainter, QPainterPath

class SplashScreen(QWidget):
    def __init__(self, image_path: str, version: str = "Version 0.1.1 (Beta Development Build)"):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.image_path = image_path
        self.version = version
        
        # 기본 스크린 크기를 이미지 비율에 대략 맞춤
        self.setFixedSize(800, 450)
        
        self.init_ui()

    def init_ui(self):
        # 전체 레이아웃 (바닥부터 쌓기 위해 하단 정렬)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 배경과 컨텐츠를 담을 래퍼
        wrapper = QWidget()
        wrapper.setFixedSize(800, 450)
        wrapper.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(40, 40, 40, 20)  # 여백
        
        # 상단 공간 (이미지 노출 영역)
        wrapper_layout.addStretch(1)
        
        # 상태 텍스트
        self.status_label = QLabel("준비 중...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #333333; font-size: 14px; font-weight: bold;")
        wrapper_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        
        # 10px 간격
        wrapper_layout.addSpacing(10)
        
        # 진행 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)  # 퍼센트 텍스트 숨김
        self.progress_bar.setFixedSize(400, 10)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #E0E0E0;
                border-radius: 5px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4DA8DA, stop:1 #12232E);
                border-radius: 5px;
            }
        """)
        wrapper_layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)
        
        # 하단 공간 및 버전 정보
        wrapper_layout.addStretch()
        
        version_label = QLabel(self.version)
        version_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        version_label.setStyleSheet("color: #666666; font-size: 11px;")
        wrapper_layout.addWidget(version_label, alignment=Qt.AlignRight | Qt.AlignBottom)
        
        layout.addWidget(wrapper)

    def paintEvent(self, event):
        # 둥근 모서리와 이미지를 배경으로 기름
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 클리핑 패스 (둥근 모서리)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        painter.setClipPath(path)
        
        # 배경 이미지 그리기
        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            # 이미지가 크면 윈도우 사이즈에 맞게 크롭/스케일
            pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            
            # 중앙을 기준으로 잘라내기 위해 여백 계산
            x_offset = (pixmap.width() - self.width()) // 2
            y_offset = (pixmap.height() - self.height()) // 2
            
            painter.drawPixmap(0, 0, pixmap, x_offset, y_offset, self.width(), self.height())
        else:
            # 원본 이미지가 없으면 기본 흰색 배경
            painter.fillPath(path, Qt.white)
            
        super().paintEvent(event)

    @Slot(str)
    def update_status(self, message: str):
        self.status_label.setText(message)

    @Slot(int)
    def update_progress(self, value: int):
        self.progress_bar.setValue(value)
