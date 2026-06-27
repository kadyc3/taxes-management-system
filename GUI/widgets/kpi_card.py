from __future__ import annotations
from typing import Optional, Literal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt


Accent = Literal["blue", "green", "orange", "red", "darkblue", "purple"]

_ICON_STYLES: dict[str, str] = {
    "blue":     "background-color: #dbeafe; color: #2563eb; border-radius: 10px; padding: 10px;",
    "green":    "background-color: #dcfce7; color: #16a34a; border-radius: 10px; padding: 10px;",
    "orange":   "background-color: #fef3c7; color: #92400e; border-radius: 10px; padding: 10px;",
    "red":      "background-color: #fee2e2; color: #dc2626; border-radius: 10px; padding: 10px;",
    "darkblue": "background-color: #e0e7ff; color: #3730a3; border-radius: 10px; padding: 10px;",
    "purple":   "background-color: #f3e8ff; color: #7c3aed; border-radius: 10px; padding: 10px;",
}


class KpiCard(QWidget):
    def __init__(
        self,
        label: str,
        value: str,
        icon_text: str = "■",
        description: str = "",
        accent: Accent = "blue",
        trend: Optional[tuple[str, bool]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("KpiCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(4)

        # top row: icon + trend
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        icon_lbl = QLabel(icon_text)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(_ICON_STYLES.get(accent, _ICON_STYLES["blue"]))
        icon_lbl.setFixedSize(40, 40)
        top_row.addWidget(icon_lbl)
        top_row.addStretch()

        if trend:
            trend_val, trend_up = trend
            arrow = "▲" if trend_up else "▼"
            bg = "#dcfce7" if trend_up else "#fee2e2"
            fg = "#16a34a" if trend_up else "#dc2626"
            trend_lbl = QLabel(f"{arrow} {trend_val}")
            trend_lbl.setStyleSheet(
                f"background-color: {bg}; color: {fg}; "
                f"border-radius: 10px; padding: 2px 8px; font-size: 11px; font-weight: 600;"
            )
            top_row.addWidget(trend_lbl)

        root.addLayout(top_row)
        root.addSpacing(12)

        value_lbl = QLabel(value)
        value_lbl.setObjectName("KpiValue")
        root.addWidget(value_lbl)

        label_lbl = QLabel(label)
        label_lbl.setObjectName("KpiLabel")
        root.addWidget(label_lbl)

        if description:
            desc_lbl = QLabel(description)
            desc_lbl.setObjectName("KpiDescription")
            root.addWidget(desc_lbl)