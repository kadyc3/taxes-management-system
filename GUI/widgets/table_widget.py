from __future__ import annotations
from typing import Optional, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QAbstractItemView, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal

from GUI.widgets.base_widgets import PrimaryButton, SecondaryButton


class ModernTable(QTableWidget):
    def __init__(
        self,
        columns: List[str],
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setHighlightSections(False)
        self.setShowGrid(False)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(200)

    def set_cell_widget_centered(self, row: int, col: int, widget: QWidget) -> None:
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(widget)
        self.setCellWidget(row, col, container)

    def add_text_item(
        self,
        row: int,
        col: int,
        text: str,
        align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
    ) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        item.setTextAlignment(align)
        self.setItem(row, col, item)
        return item


class PaginationBar(QWidget):
    page_changed = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_page = 1
        self._total_pages = 1

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        self._info_lbl = QLabel()
        self._info_lbl.setObjectName("PaginationInfo")
        layout.addWidget(self._info_lbl)
        layout.addStretch()

        self._prev_btn = self._make_btn("← Prev")
        self._prev_btn.clicked.connect(self._prev)
        layout.addWidget(self._prev_btn)

        self._page_lbl = QLabel()
        self._page_lbl.setObjectName("PaginationInfo")
        layout.addWidget(self._page_lbl)

        self._next_btn = self._make_btn("Next →")
        self._next_btn.clicked.connect(self._next)
        layout.addWidget(self._next_btn)

    def _make_btn(self, text: str) -> SecondaryButton:
        btn = SecondaryButton(text)
        btn.setObjectName("PaginationButton")
        btn.setFixedHeight(30)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def update_state(self, current: int, total_pages: int, total_rows: int, page_size: int) -> None:
        self._current_page = current
        self._total_pages = max(1, total_pages)
        start = (current - 1) * page_size + 1 if total_rows else 0
        end = min(current * page_size, total_rows)
        self._info_lbl.setText(f"Showing {start}–{end} of {total_rows} records")
        self._page_lbl.setText(f"Page {current} / {self._total_pages}")
        self._prev_btn.setEnabled(current > 1)
        self._next_btn.setEnabled(current < self._total_pages)

    def _prev(self) -> None:
        if self._current_page > 1:
            self.page_changed.emit(self._current_page - 1)

    def _next(self) -> None:
        if self._current_page < self._total_pages:
            self.page_changed.emit(self._current_page + 1)