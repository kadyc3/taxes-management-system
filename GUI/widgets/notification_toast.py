from __future__ import annotations
from typing import Optional, Literal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QFont


ToastKind = Literal["success", "error", "info", "warning"]


class NotificationToast(QWidget):
    def __init__(
        self,
        message: str,
        kind: ToastKind = "info",
        parent: Optional[QWidget] = None,
        duration_ms: int = 3000,
    ) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        obj_names = {
            "success": "ToastSuccess",
            "error": "ToastError",
            "info": "ToastInfo",
            "warning": "ToastInfo",
        }
        icons = {"success": "✓", "error": "✕", "info": "ℹ", "warning": "⚠"}

        container = QWidget(self)
        container.setObjectName(obj_names.get(kind, "ToastInfo"))
        layout = QHBoxLayout(container)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)

        icon_lbl = QLabel(icons.get(kind, "ℹ"))
        icon_lbl.setStyleSheet("font-size: 14px; background: transparent;")
        layout.addWidget(icon_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setObjectName("ToastText")
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet("background: transparent;")
        layout.addWidget(msg_lbl)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(container)
        self.setFixedWidth(340)
        self.adjustSize()

        QTimer.singleShot(duration_ms, self.close)

    def show_in(self, parent: QWidget) -> None:
        if parent:
            px = parent.x() + parent.width() - self.width() - 20
            py = parent.y() + parent.height() - self.height() - 30
            self.move(px, py)
        self.show()
        self.raise_()