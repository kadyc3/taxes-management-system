from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt

class ConfirmDialog(QDialog):
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.msg_label = QLabel(message, self)
        self.msg_label.setWordWrap(True)
        layout.addWidget(self.msg_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.confirm_btn = QPushButton("Confirm", self)
        self.confirm_btn.setObjectName("DangerButton")  # Often danger action like delete
        self.confirm_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.confirm_btn)

        layout.addLayout(btn_layout)


class RejectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reject Declaration")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.rejection_reason = ""

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel("Please enter the reason for rejecting this declaration:", self)
        label.setStyleSheet("font-weight: 600;")
        layout.addWidget(label)

        self.reason_input = QTextEdit(self)
        self.reason_input.setPlaceholderText("Enter rejection reason here...")
        self.reason_input.setMinimumHeight(100)
        layout.addWidget(self.reason_input)

        self.error_label = QLabel("", self)
        self.error_label.setStyleSheet("color: #f87171; font-weight: 500;")
        layout.addWidget(self.error_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.reject_btn = QPushButton("Reject", self)
        self.reject_btn.setObjectName("DangerButton")
        self.reject_btn.clicked.connect(self.on_reject_clicked)
        btn_layout.addWidget(self.reject_btn)

        layout.addLayout(btn_layout)

    def on_reject_clicked(self):
        reason = self.reason_input.toPlainText().strip()
        if not reason:
            self.error_label.setText("Rejection reason cannot be empty.")
            return
        
        self.rejection_reason = reason
        self.accept()
