from __future__ import annotations
from typing import Optional
from PyQt6.QtWidgets import (
    QPushButton, QLabel, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLineEdit, QComboBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor


# ── Buttons ────────────────────────────────────────────────

class PrimaryButton(QPushButton):
    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setObjectName("PrimaryButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)


class SecondaryButton(QPushButton):
    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setObjectName("SecondaryButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)


class DangerButton(QPushButton):
    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setObjectName("DangerButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)


class GhostButton(QPushButton):
    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setObjectName("GhostButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class IconButton(QPushButton):
    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setObjectName("IconButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(32, 32)


# ── Status Badge ────────────────────────────────────────────

_STATUS_OBJECT_NAMES: dict[str, str] = {
    "Active": "BadgeActive",
    "Suspended": "BadgeSuspended",
    "Deregistered": "BadgeDeregistered",
    "Draft": "BadgeDraft",
    "Submitted": "BadgeSubmitted",
    "Validated": "BadgeValidated",
    "Rejected": "BadgeRejected",
    "success": "BadgeSuccess",
    "info": "BadgeInfo",
    "warning": "BadgeWarning",
    "danger": "BadgeDanger",
}


class StatusBadge(QLabel):
    def __init__(self, status: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(status, parent)
        obj = _STATUS_OBJECT_NAMES.get(status, "BadgeInfo")
        self.setObjectName(obj)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)


# ── Card ────────────────────────────────────────────────────

class Card(QFrame):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

    def add_widget(self, widget: QWidget) -> None:
        self._layout.addWidget(widget)

    def inner_layout(self) -> QVBoxLayout:
        return self._layout


# ── Separator ───────────────────────────────────────────────

class HSeparator(QFrame):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setObjectName("DialogSeparator")
        self.setFixedHeight(1)


# ── Field Label ─────────────────────────────────────────────

class FieldLabel(QLabel):
    def __init__(self, text: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setObjectName("FieldLabel")


# ── Search bar ──────────────────────────────────────────────

class SearchBar(QLineEdit):
    def __init__(self, placeholder: str = "Search…", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("SearchBar")
        self.setPlaceholderText(placeholder)
        self.setMinimumWidth(220)
        self.setMinimumHeight(34)


# ── Filter Combobox ─────────────────────────────────────────

class FilterCombo(QComboBox):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(34)
        self.setMinimumWidth(160)


# ── Section title ───────────────────────────────────────────

class SectionTitle(QLabel):
    def __init__(self, text: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setObjectName("SectionTitle")


# ── Empty State ─────────────────────────────────────────────

class EmptyStateWidget(QWidget):
    def __init__(
        self,
        title: str = "No results found",
        description: str = "Try adjusting your search or filters.",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)

        icon = QLabel("◎", self)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 32px; color: #d1d5db;")

        title_lbl = QLabel(title, self)
        title_lbl.setObjectName("EmptyStateTitle")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc_lbl = QLabel(description, self)
        desc_lbl.setObjectName("EmptyStateDescription")
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_lbl.setWordWrap(True)

        layout.addWidget(icon)
        layout.addWidget(title_lbl)
        layout.addWidget(desc_lbl)


# ── Avatar ──────────────────────────────────────────────────

class AvatarWidget(QLabel):
    def __init__(self, initials: str, size: int = 36, parent: Optional[QWidget] = None) -> None:
        super().__init__(initials, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(QSize(size, size))
        r = size // 2
        self.setStyleSheet(
            f"background-color: #2563eb; color: #ffffff; "
            f"border-radius: {r}px; font-size: {max(10, size//3)}px; font-weight: 700;"
        )