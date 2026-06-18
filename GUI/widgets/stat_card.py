"""
GUI/widgets/stat_card.py

A reusable card widget that displays a title, a large numeric value,
and an optional subtitle. Used on the dashboard.
"""

from __future__ import annotations
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class StatCard(QFrame):
    """
    A compact statistics card.

    Parameters
    ----------
    title   : str   — label shown above the value (e.g. "Total Taxpayers")
    value   : str   — large numeric or text value (e.g. "142")
    subtitle: str   — smaller text below the value (optional)
    color   : str   — hex color for the value label accent
    """

    def __init__(
        self,
        title: str,
        value: str = "0",
        subtitle: str = "",
        color: str = "#1A6B3C",
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._color = color
        self._setup_ui(title, value, subtitle)

    def _setup_ui(self, title: str, value: str, subtitle: str) -> None:
        self.setObjectName("StatCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(160)
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        # Title
        self._title_label = QLabel(title)
        self._title_label.setObjectName("StatCardTitle")
        title_font = QFont()
        title_font.setPointSize(9)
        self._title_label.setFont(title_font)
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Value
        self._value_label = QLabel(value)
        self._value_label.setObjectName("StatCardValue")
        value_font = QFont()
        value_font.setPointSize(26)
        value_font.setBold(True)
        self._value_label.setFont(value_font)
        self._value_label.setStyleSheet(f"color: {self._color};")
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Subtitle
        self._subtitle_label = QLabel(subtitle)
        self._subtitle_label.setObjectName("StatCardSubtitle")
        sub_font = QFont()
        sub_font.setPointSize(8)
        self._subtitle_label.setFont(sub_font)
        self._subtitle_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(self._title_label)
        layout.addWidget(self._value_label)
        if subtitle:
            layout.addWidget(self._subtitle_label)
        layout.addStretch()

    # ------------------------------------------------------------------
    # Public update API
    # ------------------------------------------------------------------
    def set_value(self, value: str) -> None:
        self._value_label.setText(value)

    def set_subtitle(self, subtitle: str) -> None:
        self._subtitle_label.setText(subtitle)