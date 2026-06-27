from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QLabel, QFrame, QButtonGroup
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from .pages.dashboard_page import DashboardPage
from .pages.taxpayer_page import TaxpayerPage
from .pages.declaration_page import DeclarationPage

class DashboardWindow(QMainWindow):
    def __init__(self, auth_service, taxpayer_service, declaration_service, dashboard_service, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.taxpayer_service = taxpayer_service
        self.declaration_service = declaration_service
        self.dashboard_service = dashboard_service
        self.current_user = auth_service.get_current_user()

        self.setWindowTitle("Taxes Management System")
        self.resize(1100, 750)
        self.setMinimumSize(950, 650)

        # Central Widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Sidebar Container
        sidebar = QFrame(self)
        sidebar.setObjectName("SidebarFrame")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 25, 15, 25)
        sidebar_layout.setSpacing(10)

        # Application Logo/Title in Sidebar
        logo_label = QLabel("TAX PORTAL", sidebar)
        logo_label.setObjectName("SidebarTitle")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(logo_label)

        line = QFrame(sidebar)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #334155; max-height: 1px; margin-bottom: 15px;")
        sidebar_layout.addWidget(line)

        # Navigation Buttons Group
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        self.dash_btn = QPushButton("  📊   Dashboard", sidebar)
        self.dash_btn.setCheckable(True)
        self.dash_btn.setChecked(True)
        self.dash_btn.setProperty("class", "SidebarBtn")
        self.dash_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dash_btn.setObjectName("SidebarBtn")
        self.nav_group.addButton(self.dash_btn, 0)
        sidebar_layout.addWidget(self.dash_btn)

        self.tax_btn = QPushButton("  👤   Taxpayers", sidebar)
        self.tax_btn.setCheckable(True)
        self.tax_btn.setProperty("class", "SidebarBtn")
        self.tax_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tax_btn.setObjectName("SidebarBtn")
        self.nav_group.addButton(self.tax_btn, 1)
        sidebar_layout.addWidget(self.tax_btn)

        self.dec_btn = QPushButton("  🧾   Declarations", sidebar)
        self.dec_btn.setCheckable(True)
        self.dec_btn.setProperty("class", "SidebarBtn")
        self.dec_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dec_btn.setObjectName("SidebarBtn")
        self.nav_group.addButton(self.dec_btn, 2)
        sidebar_layout.addWidget(self.dec_btn)

        sidebar_layout.addStretch()

        # User Profile info inside Sidebar Bottom
        user_info_frame = QFrame(sidebar)
        user_info_frame.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        user_info_layout = QVBoxLayout(user_info_frame)
        user_info_layout.setSpacing(4)
        user_info_layout.setContentsMargins(6, 6, 6, 6)

        user_name_lbl = QLabel(f"👤  {self.current_user.username}", user_info_frame)
        user_name_lbl.setStyleSheet("font-weight: bold; color: #f8fafc; font-size: 13px;")
        user_info_layout.addWidget(user_name_lbl)

        role_lbl = QLabel(f"Role: {self.current_user.role.value.upper()}", user_info_frame)
        role_lbl.setStyleSheet("color: #94a3b8; font-size: 11px;")
        user_info_layout.addWidget(role_lbl)

        sidebar_layout.addWidget(user_info_frame)

        # Logout button
        logout_btn = QPushButton("  🚪   Logout", sidebar)
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b181a;
                border: 1px solid #7f1d1d;
                border-radius: 6px;
                color: #f87171;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #7f1d1d;
                color: #ffffff;
            }
        """)
        logout_btn.clicked.connect(self.on_logout_clicked)
        sidebar_layout.addWidget(logout_btn)

        main_layout.addWidget(sidebar)

        # 2. Main Content Viewport
        content_pane = QFrame(self)
        content_pane.setObjectName("ContentFrame")
        content_layout = QVBoxLayout(content_pane)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top Header Bar
        header = QFrame(content_pane)
        header.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        self.page_title_lbl = QLabel("Dashboard", header)
        self.page_title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #f8fafc;")
        header_layout.addWidget(self.page_title_lbl)

        header_layout.addStretch()

        app_title_lbl = QLabel("TAXES MANAGEMENT SYSTEM", header)
        app_title_lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #475569; letter-spacing: 1px;")
        header_layout.addWidget(app_title_lbl)

        content_layout.addWidget(header)

        # Stacked Pages Widget
        self.pages_stack = QStackedWidget(content_pane)
        
        # Pages init
        self.dashboard_page = DashboardPage(self.dashboard_service, self.pages_stack)
        self.taxpayer_page = TaxpayerPage(self.taxpayer_service, self.current_user, self.pages_stack)
        self.declaration_page = DeclarationPage(self.declaration_service, self.taxpayer_service, self.current_user, self.pages_stack)

        self.pages_stack.addWidget(self.dashboard_page)      # Index 0
        self.pages_stack.addWidget(self.taxpayer_page)       # Index 1
        self.pages_stack.addWidget(self.declaration_page)    # Index 2

        content_layout.addWidget(self.pages_stack, 1)
        main_layout.addWidget(content_pane, 1)

        # Signals
        self.nav_group.idClicked.connect(self.on_navigation_clicked)

    def on_navigation_clicked(self, page_id: int):
        self.pages_stack.setCurrentIndex(page_id)
        
        # Refresh target page data and set title
        if page_id == 0:
            self.page_title_lbl.setText("Dashboard")
            self.dashboard_page.refresh_data()
        elif page_id == 1:
            self.page_title_lbl.setText("Taxpayers")
            self.taxpayer_page.refresh_list()
        elif page_id == 2:
            self.page_title_lbl.setText("Declarations")
            self.declaration_page.refresh_list()

    def on_logout_clicked(self):
        self.auth_service.logout()
        self.close()
