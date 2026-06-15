from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class LoginWindow(QWidget):

    def __init__(self, auth_service, on_login_success):
        """
        auth_service     → injected AuthService instance
        on_login_success → callback function(user) called after login
        """
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

        # Title
        title = QLabel("🏛️ Taxes Management System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFixedHeight(36)
        layout.addWidget(self.username_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(36)
        layout.addWidget(self.password_input)

        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.setFixedHeight(40)
        self.login_btn.clicked.connect(self._handle_login)
        # Allow pressing Enter to login
        self.password_input.returnPressed.connect(self._handle_login)
        layout.addWidget(self.login_btn)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def _handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.status_label.setText("Please enter both username and password.")
            return

        user = self.auth_service.login(username, password)

        if user is None:
            self.status_label.setText("❌ Invalid username or password.")
            self.password_input.clear()
        else:
            self.on_login_success(user)