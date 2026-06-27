from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from Kernel.exceptions.app_exceptions import AuthenticationError

class LoginWindow(QDialog):
    def __init__(self, auth_service, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.user = None

        self.setWindowTitle("Login - Taxes Management System")
        self.setModal(True)
        self.setFixedSize(380, 480)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 40, 30, 30)
        layout.setSpacing(15)

        # Title Label
        title_label = QLabel("TAXES MANAGEMENT", self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: 800; color: #38bdf8; letter-spacing: 1px;")
        layout.addWidget(title_label)

        subtitle_label = QLabel("Desktop Application Portal", self)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 11px; color: #94a3b8; font-weight: 500;")
        layout.addWidget(subtitle_label)

        layout.addSpacing(15)

        # Username Input
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(40)
        layout.addWidget(self.username_input)

        # Password Input
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)
        self.password_input.returnPressed.connect(self.on_login_clicked)
        layout.addWidget(self.password_input)

        # Error message label
        self.error_label = QLabel("", self)
        self.error_label.setStyleSheet("color: #f87171; font-weight: 500; font-size: 12px;")
        self.error_label.setWordWrap(True)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)

        # Login button
        self.login_btn = QPushButton("Login", self)
        self.login_btn.setObjectName("PrimaryButton")
        self.login_btn.setMinimumHeight(40)
        self.login_btn.clicked.connect(self.on_login_clicked)
        layout.addWidget(self.login_btn)

        layout.addStretch()

        # Quick login helper box (Useful for testing)
        helper_frame = QFrame(self)
        helper_frame.setObjectName("CardFrame")
        helper_frame.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 1px dashed #475569;
                border-radius: 6px;
            }
        """)
        helper_layout = QVBoxLayout(helper_frame)
        helper_layout.setContentsMargins(10, 10, 10, 10)
        helper_layout.setSpacing(5)

        helper_title = QLabel("Quick Login (For Testing)", helper_frame)
        helper_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #94a3b8; border: none;")
        helper_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        helper_layout.addWidget(helper_title)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(5)

        admin_quick = QPushButton("Admin", helper_frame)
        admin_quick.setStyleSheet("font-size: 11px; padding: 4px; background-color: #334155; border: none;")
        admin_quick.clicked.connect(lambda: self.fill_credentials("admin", "admin123"))
        
        editor_quick = QPushButton("Editor", helper_frame)
        editor_quick.setStyleSheet("font-size: 11px; padding: 4px; background-color: #334155; border: none;")
        editor_quick.clicked.connect(lambda: self.fill_credentials("editor", "editor123"))
        
        user_quick = QPushButton("User", helper_frame)
        user_quick.setStyleSheet("font-size: 11px; padding: 4px; background-color: #334155; border: none;")
        user_quick.clicked.connect(lambda: self.fill_credentials("user", "user123"))

        btn_row.addWidget(admin_quick)
        btn_row.addWidget(editor_quick)
        btn_row.addWidget(user_quick)
        helper_layout.addLayout(btn_row)

        layout.addWidget(helper_frame)

    def fill_credentials(self, username, password):
        self.username_input.setText(username)
        self.password_input.setText(password)
        self.on_login_clicked()

    def on_login_clicked(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.error_label.setText("Please enter both username and password.")
            return

        try:
            self.user = self.auth_service.login(username, password)
            self.accept()
        except AuthenticationError as e:
            self.error_label.setText(str(e))
        except Exception as e:
            self.error_label.setText(f"Login error: {str(e)}")
