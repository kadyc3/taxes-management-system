"""
GUI/widgets/search_bar.py

A search bar that emits a `search_triggered` signal when the user
types (with a small debounce) or presses Enter / the search button.
"""

from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PyQt6.QtCore import pyqtSignal, QTimer


class SearchBar(QWidget):
    """
    Emits search_triggered(str) when the user changes the query.
    The signal is debounced by 350 ms to avoid hitting the DB on every keystroke.
    """

    search_triggered = pyqtSignal(str)

    def __init__(self, placeholder: str = "Search…", parent=None) -> None:
        super().__init__(parent)
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(350)
        self._debounce_timer.timeout.connect(self._emit_search)
        self._setup_ui(placeholder)

    def _setup_ui(self, placeholder: str) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._input = QLineEdit()
        self._input.setPlaceholderText(placeholder)
        self._input.setMinimumHeight(34)
        self._input.textChanged.connect(self._on_text_changed)
        self._input.returnPressed.connect(self._emit_search)

        self._btn = QPushButton("Search")
        self._btn.setObjectName("SearchButton")
        self._btn.setMinimumHeight(34)
        self._btn.clicked.connect(self._emit_search)

        layout.addWidget(self._input, stretch=1)
        layout.addWidget(self._btn)

    def _on_text_changed(self) -> None:
        self._debounce_timer.start()

    def _emit_search(self) -> None:
        self._debounce_timer.stop()
        self.search_triggered.emit(self._input.text().strip())

    def text(self) -> str:
        return self._input.text().strip()

    def clear(self) -> None:
        self._input.clear()