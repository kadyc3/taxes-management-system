from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from Kernel.models.user import User

class DashboardWindow(QWidget):

    def __init__(self, user: User):
        super().__init__()
        self.user = user
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Dashboard")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Welcome message
        welcome = QLabel(f"Welcome, {self.user.full_name}!")
        welcome.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome)

        # Role badge
        role_label = QLabel(f"Role: {self.user.role.value.upper()}")
        role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        role_label.setFont(QFont("Arial", 12))
        role_label.setStyleSheet(self._role_color())
        layout.addWidget(role_label)

        # Placeholder content area
        info = QLabel("📋 Dashboard content will appear here in next milestones.")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)

        self.setLayout(layout)

    def _role_color(self) -> str:
        colors = {
            "admin":  "color: darkred; font-weight: bold;",
            "agent":  "color: darkblue; font-weight: bold;",
            "viewer": "color: darkgreen; font-weight: bold;",
        }
        return colors.get(self.user.role.value, "")