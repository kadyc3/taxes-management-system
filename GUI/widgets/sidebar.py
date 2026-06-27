from __future__ import annotations
from typing import Optional, Callable
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QSpacerItem, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from GUI.widgets.base_widgets import AvatarWidget


NAV_ITEMS = [
    ("dashboard",    "Dashboard",    "⊞"),
    ("taxpayers",    "Taxpayers",    "♟"),
    ("declarations", "Declarations", "◫"),
    ("reports",      "Reports",      "▤"),
    ("audit_logs",   "Audit Logs",   "≡"),
    ("settings",     "Settings",     "⚙"),
]


class NavButton(QPushButton):
    def __init__(
        self,
        page_id: str,
        label: str,
        icon_ch: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.page_id = page_id
        self.setObjectName("NavButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(False)
        self.setMinimumHeight(38)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        self._icon_lbl = QLabel(icon_ch)
        self._icon_lbl.setStyleSheet("font-size: 14px; background: transparent;")
        self._icon_lbl.setFixedWidth(18)
        layout.addWidget(self._icon_lbl)

        self._text_lbl = QLabel(label)
        self._text_lbl.setStyleSheet("background: transparent; font-size: 13px; font-weight: 500;")
        layout.addWidget(self._text_lbl)
        layout.addStretch()

    def set_active(self, active: bool) -> None:
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        if active:
            self._icon_lbl.setStyleSheet("font-size: 14px; background: transparent; color: #2563eb;")
            self._text_lbl.setStyleSheet(
                "background: transparent; font-size: 13px; font-weight: 600; color: #2563eb;"
            )
        else:
            self._icon_lbl.setStyleSheet("font-size: 14px; background: transparent; color: #64748b;")
            self._text_lbl.setStyleSheet(
                "background: transparent; font-size: 13px; font-weight: 500; color: #64748b;"
            )


class Sidebar(QWidget):
    page_changed = pyqtSignal(str)
    logout_requested = pyqtSignal()

    def __init__(
        self,
        current_page: str = "dashboard",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(240)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Logo bar
        logo_bar = QWidget()
        logo_bar.setFixedHeight(64)
        logo_bar.setStyleSheet("background: transparent;")
        logo_layout = QHBoxLayout(logo_bar)
        logo_layout.setContentsMargins(20, 0, 16, 0)

        icon_box = QLabel("⚖")
        icon_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_box.setFixedSize(36, 36)
        icon_box.setStyleSheet(
            "background: qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            "stop:0 #2563eb, stop:1 #1e3a8a);"
            "border-radius: 10px; color: white; font-size: 16px;"
        )

        name_lbl = QLabel()
        name_lbl.setTextFormat(Qt.TextFormat.RichText)
        name_lbl.setText('<span style="color:#1e293b;font-size:15px;font-weight:700;">Tax</span>'
                         '<span style="color:#2563eb;font-size:15px;font-weight:700;">Admin</span>')
        logo_layout.addWidget(icon_box)
        logo_layout.addSpacing(8)
        logo_layout.addWidget(name_lbl)
        logo_layout.addStretch()
        root.addWidget(logo_bar)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #e2e8f0;")
        sep.setFixedHeight(1)
        root.addWidget(sep)

        # Nav section label
        nav_container = QWidget()
        nav_container.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(12, 12, 12, 4)
        nav_layout.setSpacing(2)

        section_lbl = QLabel("MENU")
        section_lbl.setObjectName("SidebarSection")
        section_lbl.setStyleSheet(
            "font-size: 10px; font-weight: 700; letter-spacing: 1px;"
            " color: #94a3b8; padding: 4px 4px 8px;"
        )
        nav_layout.addWidget(section_lbl)

        self._nav_buttons: list[NavButton] = []
        for page_id, label, icon_ch in NAV_ITEMS:
            btn = NavButton(page_id, label, icon_ch)
            btn.clicked.connect(lambda checked, pid=page_id: self._on_nav(pid))
            nav_layout.addWidget(btn)
            self._nav_buttons.append(btn)

        root.addWidget(nav_container)
        root.addStretch()

        # Bottom: user card + logout
        bottom = QWidget()
        bottom.setStyleSheet("background: transparent;")
        bot_layout = QVBoxLayout(bottom)
        bot_layout.setContentsMargins(12, 8, 12, 12)
        bot_layout.setSpacing(4)

        user_card = QFrame()
        user_card.setObjectName("SidebarUserCard")
        user_card_layout = QHBoxLayout(user_card)
        user_card_layout.setContentsMargins(10, 10, 10, 10)
        user_card_layout.setSpacing(10)

        avatar = AvatarWidget("AD", size=36)
        user_card_layout.addWidget(avatar)

        info = QVBoxLayout()
        info.setSpacing(1)
        name = QLabel("Admin")
        name.setObjectName("SidebarUserName")
        email = QLabel("admin@taxadmin.tn")
        email.setObjectName("SidebarUserEmail")
        info.addWidget(name)
        info.addWidget(email)
        user_card_layout.addLayout(info)
        user_card_layout.addStretch()
        bot_layout.addWidget(user_card)

        logout_btn = QPushButton("⬡  Logout")
        logout_btn.setObjectName("LogoutButton")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setMinimumHeight(36)
        logout_btn.clicked.connect(self.logout_requested.emit)
        bot_layout.addWidget(logout_btn)

        root.addWidget(bottom)

        self.set_page(current_page)

    def set_page(self, page_id: str) -> None:
        for btn in self._nav_buttons:
            btn.set_active(btn.page_id == page_id)

    def _on_nav(self, page_id: str) -> None:
        self.set_page(page_id)
        self.page_changed.emit(page_id)