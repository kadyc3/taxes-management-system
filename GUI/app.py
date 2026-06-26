"""
GUI/app.py

Main application shell (modern SaaS architecture)
- Sidebar navigation
- QStackedWidget pages
- Clean separation of UI pages
"""

from PyQt6.QtWidgets import (
    QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QStackedWidget
)

from PyQt6.QtCore import Qt

from GUI.pages.dashboard_page import DashboardPage
from GUI.pages.taxpayer_page import TaxpayerPage
from GUI.pages.declaration_page import DeclarationPage


class AppWindow(QMainWindow):

    def __init__(
        self,
        auth_service,
        dashboard_service,
        taxpayer_service,
        declaration_service,
        on_logout,
    ):
        super().__init__()

        self.auth_service = auth_service
        self.dashboard_service = dashboard_service
        self.taxpayer_service = taxpayer_service
        self.declaration_service = declaration_service
        self.on_logout = on_logout

        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self):

        self.setWindowTitle("Taxes Management System")
        self.resize(1200, 750)
        self.setMinimumSize(1000, 650)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # =========================
        # STACK (pages)
        # =========================
        self.stack = QStackedWidget()

        self.dashboard_page = DashboardPage(self.dashboard_service)
        self.taxpayer_page = TaxpayerPage(self.taxpayer_service)
        self.declaration_page = DeclarationPage(
            self.declaration_service,
            self.taxpayer_service,
            self.auth_service
        )

        self.stack.addWidget(self.dashboard_page)     # 0
        self.stack.addWidget(self.taxpayer_page)      # 1
        self.stack.addWidget(self.declaration_page)   # 2

        layout.addWidget(self.stack)
        

        # start page
        self.stack.setCurrentIndex(0)
        sidebar = QWidget()
        side_layout = QVBoxLayout(sidebar)

        btn1 = QPushButton("Dashboard")
        btn2 = QPushButton("Taxpayers")
        btn3 = QPushButton("Declarations")

        btn1.clicked.connect(self.go_dashboard)
        btn2.clicked.connect(self.go_taxpayers)
        btn3.clicked.connect(self.go_declarations)

        side_layout.addWidget(btn1)
        side_layout.addWidget(btn2)
        side_layout.addWidget(btn3)

        layout.addWidget(sidebar)

    # ---------------- NAVIGATION ----------------
    def go_dashboard(self):
        self.dashboard_page.refresh()
        self.stack.setCurrentIndex(0)

    def go_taxpayers(self):
        self.stack.setCurrentIndex(1)

    def go_declarations(self):
        self.stack.setCurrentIndex(2)