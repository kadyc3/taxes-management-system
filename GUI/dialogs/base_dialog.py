from __future__ import annotations
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QWidget, QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from GUI.widgets.base_widgets import HSeparator, PrimaryButton, SecondaryButton


class BaseDialog(QDialog):
    def __init__(
        self,
        title: str,
        subtitle: str = "",
        parent: Optional[QWidget] = None,
        min_width: int = 480,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("DialogBase")
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setMinimumWidth(min_width)

        # Outer shadow wrapper
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self._card = QFrame()
        self._card.setObjectName("DialogBase")
        self._card.setStyleSheet(
            "QFrame#DialogBase { background-color: #ffffff; border: 1px solid #e2e8f0;"
            " border-radius: 16px; }"
        )
        outer.addWidget(self._card)

        self._root = QVBoxLayout(self._card)
        self._root.setContentsMargins(28, 24, 28, 24)
        self._root.setSpacing(0)

        # Header
        header = QVBoxLayout()
        header.setSpacing(4)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)

        self._title_lbl = QLabel(title)
        self._title_lbl.setObjectName("DialogTitle")
        title_row.addWidget(self._title_lbl)
        title_row.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(
            "QPushButton { background: #f1f5f9; border: none; border-radius: 8px;"
            " color: #64748b; font-size: 12px; font-weight: bold; }"
            "QPushButton:hover { background: #e2e8f0; color: #374151; }"
        )
        close_btn.clicked.connect(self.reject)
        title_row.addWidget(close_btn)
        header.addLayout(title_row)

        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setObjectName("DialogSubtitle")
            header.addWidget(sub_lbl)

        self._root.addLayout(header)
        self._root.addSpacing(16)
        self._root.addWidget(HSeparator())
        self._root.addSpacing(20)

        # Content area
        self._content = QVBoxLayout()
        self._content.setSpacing(12)
        self._root.addLayout(self._content)

    def add_content_widget(self, widget: QWidget) -> None:
        self._content.addWidget(widget)

    def add_content_layout(self, layout) -> None:
        self._content.addLayout(layout)

    def add_button_row(self, *buttons) -> None:
        self._root.addSpacing(20)
        self._root.addWidget(HSeparator())
        self._root.addSpacing(16)
        row = QHBoxLayout()
        row.addStretch()
        for btn in buttons:
            row.addWidget(btn)
        self._root.addLayout(row)