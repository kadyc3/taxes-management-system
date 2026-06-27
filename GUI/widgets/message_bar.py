from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import QTimer, Qt

class MessageBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        
        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("font-weight: 500; font-size: 13px; border: none; background: transparent;")
        layout.addWidget(self.label, 1)
        
        self.close_btn = QPushButton("×", self)
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: inherit;
                font-size: 18px;
                font-weight: bold;
                padding: 0px;
                min-height: 20px;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)
        self.close_btn.clicked.connect(self.hide_message)
        layout.addWidget(self.close_btn)
        
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_message)

    def show_message(self, text: str, msg_type: str = "success", duration_ms: int = 5000):
        self.label.setText(text)
        
        if msg_type == "success":
            # Emerald green palette
            self.setStyleSheet("""
                background-color: #064e3b;
                color: #34d399;
                border: 1px solid #059669;
                border-radius: 6px;
            """)
        elif msg_type == "error":
            # Crimson rose palette
            self.setStyleSheet("""
                background-color: #7f1d1d;
                color: #f87171;
                border: 1px solid #dc2626;
                border-radius: 6px;
            """)
        elif msg_type == "warning":
            # Amber orange palette
            self.setStyleSheet("""
                background-color: #78350f;
                color: #fbbf24;
                border: 1px solid #d97706;
                border-radius: 6px;
            """)
        else:
            # Slate blue palette
            self.setStyleSheet("""
                background-color: #1e3a8a;
                color: #60a5fa;
                border: 1px solid #2563eb;
                border-radius: 6px;
            """)
            
        self.setVisible(True)
        if duration_ms > 0:
            self.timer.start(duration_ms)

    def hide_message(self):
        self.timer.stop()
        self.setVisible(False)
