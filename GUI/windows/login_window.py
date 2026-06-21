from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from Kernel.exceptions.authentication_exception import AuthenticationException


class LoginWindow(QWidget):

    def __init__(self, auth_service, on_login_success):
        super().__init__()

        self.auth_service = auth_service
        self.on_login_success = on_login_success

        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Taxes Management System — Login")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)

        title = QLabel("🏛️ Taxes Management System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self._handle_login)
        layout.addWidget(self.login_btn)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def _handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username:
            self.status_label.setText("Enter username")
            return

        if not password:
            self.status_label.setText("Enter password")
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("Signing in...")

        try:
            user = self.auth_service.login(username, password)
            self.on_login_success(user)

        except AuthenticationException as e:
            self.status_label.setText(str(e))

        finally:
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Login")