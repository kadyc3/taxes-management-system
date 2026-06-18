"""
GUI/widgets/message_bar.py

An inline dismissible notification bar used throughout the application
to show success, error, or informational messages without modal dialogs.
"""

from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer


_STYLES = {
    "success": "background:#D4EDDA; color:#155724; border:1px solid #C3E6CB; border-radius:4px;",
    "error":   "background:#F8D7DA; color:#721C24; border:1px solid #F5C6CB; border-radius:4px;",
    "info":    "background:#D1ECF1; color:#0C5460; border:1px solid #BEE5EB; border-radius:4px;",
    "warning": "background:#FFF3CD; color:#856404; border:1px solid #FFEEBA; border-radius:4px;",
}


class MessageBar(QWidget):
    """
    Show a message banner that auto-dismisses after `timeout_ms` ms.
    Pass timeout_ms=0 to keep it visible until the user closes it.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)
        self._setup_ui()
        self.hide()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)

        self._label = QLabel()
        self._label.setWordWrap(True)
        self._label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        self._close_btn = QPushButton("✕")
        self._close_btn.setFixedSize(20, 20)
        self._close_btn.setFlat(True)
        self._close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close_btn.clicked.connect(self.hide)

        layout.addWidget(self._label, stretch=1)
        layout.addWidget(self._close_btn)

    def show_message(self, text: str, kind: str = "info", timeout_ms: int = 4000) -> None:
        self._label.setText(text)
        self.setStyleSheet(_STYLES.get(kind, _STYLES["info"]))
        self.show()
        self._timer.stop()
        if timeout_ms > 0:
            self._timer.start(timeout_ms)

    def show_success(self, text: str, timeout_ms: int = 4000) -> None:
        self.show_message(text, "success", timeout_ms)

    def show_error(self, text: str, timeout_ms: int = 0) -> None:
        self.show_message(text, "error", timeout_ms)

    def show_info(self, text: str, timeout_ms: int = 4000) -> None:
        self.show_message(text, "info", timeout_ms)