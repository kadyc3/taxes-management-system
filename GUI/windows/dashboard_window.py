"""
GUI/windows/dashboard_window.py

The main application window after login.
Contains:
  - A persistent left sidebar with navigation buttons
  - A QStackedWidget that holds all content pages
  - Dashboard summary page
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QStackedWidget, QPushButton, QFrame,
    QScrollArea, QSizePolicy, QSpacerItem,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from Kernel.models.user import User
from Kernel.services.auth_service import AuthService
from Kernel.services.dashboard_service import DashboardService
from GUI.widgets.stat_card import StatCard


class DashboardWindow(QMainWindow):
    """
    Parameters
    ----------
    auth_service      : AuthService
    dashboard_service : DashboardService
    taxpayer_page     : QWidget   — injected by AppController
    declaration_page  : QWidget   — injected by AppController
    on_logout         : callable  — called when user logs out
    """

    def __init__(
        self,
        auth_service: AuthService,
        dashboard_service: DashboardService,
        taxpayer_page: QWidget,
        declaration_page: QWidget,
        on_logout,
    ) -> None:
        super().__init__()
        self._auth = auth_service
        self._dashboard_svc = dashboard_service
        self._taxpayer_page = taxpayer_page
        self._declaration_page = declaration_page
        self._on_logout = on_logout

        self._setup_window()
        self._build_ui()
        self._show_dashboard()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------
    def _setup_window(self) -> None:
        user: User = self._auth.current_user
        self.setWindowTitle(f"Taxes Management System — {user.username}")
        self.setMinimumSize(1024, 680)
        self.resize(1200, 750)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar ---
        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar)

        # --- Content stack ---
        self._stack = QStackedWidget()
        self._dashboard_page = self._build_dashboard_page()
        self._stack.addWidget(self._dashboard_page)   # index 0
        self._stack.addWidget(self._taxpayer_page)    # index 1
        self._stack.addWidget(self._declaration_page) # index 2

        main_layout.addWidget(self._stack, stretch=1)

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(210)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # App title
        title_label = QLabel("⚖ TaxAdmin")
        title_label.setObjectName("SidebarTitle")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title_label.setFont(title_font)

        user: User = self._auth.current_user
        role_label = QLabel(f"{user.username}\n{user.role}")
        role_label.setObjectName("SidebarSubtitle")
        role_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(role_label)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("color: #1E4A7A; margin: 0 12px;")
        layout.addWidget(div)
        layout.addSpacing(8)

        # Nav buttons (checkable so only one is active)
        self._nav_buttons: list[QPushButton] = []

        def make_nav(label: str, index: int) -> QPushButton:
            btn = QPushButton(label)
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setMinimumHeight(44)
            btn.clicked.connect(lambda _, i=index: self._navigate(i))
            self._nav_buttons.append(btn)
            layout.addWidget(btn)
            return btn

        make_nav("📊  Dashboard", 0)
        make_nav("🏢  Taxpayers", 1)
        make_nav("📄  Declarations", 2)

        layout.addStretch()

        # Logout
        logout_btn = QPushButton("⬅  Logout")
        logout_btn.setObjectName("LogoutButton")
        logout_btn.setMinimumHeight(44)
        logout_btn.clicked.connect(self._handle_logout)
        layout.addWidget(logout_btn)
        layout.addSpacing(8)

        return sidebar

    def _build_dashboard_page(self) -> QWidget:
        """Build the embedded dashboard summary page."""
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(20)

        # Header
        header_row = QHBoxLayout()
        page_title = QLabel("Dashboard")
        page_title.setObjectName("PageTitle")
        page_subtitle = QLabel("Overview of tax administration activity")
        page_subtitle.setObjectName("PageSubtitle")
        header_col = QVBoxLayout()
        header_col.setSpacing(2)
        header_col.addWidget(page_title)
        header_col.addWidget(page_subtitle)
        header_row.addLayout(header_col)
        header_row.addStretch()

        refresh_btn = QPushButton("↻  Refresh")
        refresh_btn.setObjectName("SecondaryButton")
        refresh_btn.setMinimumHeight(34)
        refresh_btn.setFixedWidth(110)
        refresh_btn.clicked.connect(self._refresh_dashboard)
        header_row.addWidget(refresh_btn)
        outer.addLayout(header_row)

        # Taxpayer cards row
        tp_section_label = QLabel("Taxpayers")
        tp_section_label.setStyleSheet(
            "font-weight: bold; font-size: 10pt; color: #0F3460; margin-top: 4px;"
        )
        outer.addWidget(tp_section_label)

        tp_row = QHBoxLayout()
        tp_row.setSpacing(14)
        self._card_tp_total = StatCard("Total Taxpayers", "—", "", "#0F3460")
        self._card_tp_active = StatCard("Active", "—", "", "#1A6B3C")
        self._card_tp_suspended = StatCard("Suspended", "—", "", "#C0392B")
        self._card_tp_dereg = StatCard("Deregistered", "—", "", "#777777")
        for card in (
            self._card_tp_total,
            self._card_tp_active,
            self._card_tp_suspended,
            self._card_tp_dereg,
        ):
            tp_row.addWidget(card)
        outer.addLayout(tp_row)

        # Declaration cards row
        decl_section_label = QLabel("Declarations")
        decl_section_label.setStyleSheet(
            "font-weight: bold; font-size: 10pt; color: #0F3460; margin-top: 8px;"
        )
        outer.addWidget(decl_section_label)

        decl_row = QHBoxLayout()
        decl_row.setSpacing(14)
        self._card_decl_total = StatCard("Total Declarations", "—", "", "#0F3460")
        self._card_decl_draft = StatCard("Draft", "—", "", "#856404")
        self._card_decl_submitted = StatCard("Submitted", "—", "", "#0C5460")
        self._card_decl_validated = StatCard("Validated", "—", "", "#1A6B3C")
        self._card_decl_rejected = StatCard("Rejected", "—", "", "#C0392B")
        for card in (
            self._card_decl_total,
            self._card_decl_draft,
            self._card_decl_submitted,
            self._card_decl_validated,
            self._card_decl_rejected,
        ):
            decl_row.addWidget(card)
        outer.addLayout(decl_row)

        # Total due card (full width)
        due_row = QHBoxLayout()
        self._card_total_due = StatCard(
            "Total Amount Due (TND)", "—", "Across all declarations", "#8B0000"
        )
        self._card_total_due.setMinimumHeight(90)
        due_row.addWidget(self._card_total_due)
        due_row.addStretch()
        outer.addLayout(due_row)

        # Recent activity label
        activity_label = QLabel("Recent Activity")
        activity_label.setStyleSheet(
            "font-weight: bold; font-size: 10pt; color: #0F3460; margin-top: 8px;"
        )
        outer.addWidget(activity_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(180)
        scroll.setStyleSheet("border: 1px solid #E0E8F0; border-radius: 4px;")

        self._activity_container = QWidget()
        self._activity_layout = QVBoxLayout(self._activity_container)
        self._activity_layout.setContentsMargins(12, 8, 12, 8)
        self._activity_layout.setSpacing(4)
        scroll.setWidget(self._activity_container)
        outer.addWidget(scroll)

        outer.addStretch()
        return page

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def _navigate(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == index)
        if index == 0:
            self._refresh_dashboard()

    def _show_dashboard(self) -> None:
        self._navigate(0)

    # ------------------------------------------------------------------
    # Dashboard data refresh
    # ------------------------------------------------------------------
    def _refresh_dashboard(self) -> None:
        try:
            summary = self._dashboard_svc.get_summary()
        except Exception:
            return

        tp = summary["taxpayers"]
        self._card_tp_total.set_value(str(tp["total"]))
        self._card_tp_active.set_value(str(tp["active"]))
        self._card_tp_suspended.set_value(str(tp["suspended"]))
        self._card_tp_dereg.set_value(str(tp["deregistered"]))

        decl = summary["declarations"]
        self._card_decl_total.set_value(str(decl["total"]))
        self._card_decl_draft.set_value(str(decl["draft"]))
        self._card_decl_submitted.set_value(str(decl["submitted"]))
        self._card_decl_validated.set_value(str(decl["validated"]))
        self._card_decl_rejected.set_value(str(decl["rejected"]))
        self._card_total_due.set_value(f"{decl['total_due']:,.3f}")

        # Recent activity
        for i in reversed(range(self._activity_layout.count())):
            widget = self._activity_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for log in summary["recent_activity"]:
            text = f"[{log.created_at.strftime('%Y-%m-%d %H:%M')}]  {log.action} {log.entity_type} #{log.entity_id} {log.details or ''}"
            lbl = QLabel(text)
            lbl.setStyleSheet("font-size: 8pt; color: #555;")
            self._activity_layout.addWidget(lbl)

        if not summary["recent_activity"]:
            empty = QLabel("No activity recorded yet.")
            empty.setStyleSheet("font-size: 8pt; color: #AAA;")
            self._activity_layout.addWidget(empty)

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------
    def _handle_logout(self) -> None:
        self._auth.logout()
        self.close()
        self._on_logout()

