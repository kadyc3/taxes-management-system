from PyQt6.QtWidgets import QLineEdit, QCompleter
from PyQt6.QtCore import Qt
from typing import List

class SearchBar(QLineEdit):
    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setClearButtonEnabled(True)
        self.setObjectName("SearchBar")

    def set_autocomplete_list(self, items: List[str]):
        completer = QCompleter(items, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        # Style the completer popup list
        popup = completer.popup()
        popup.setStyleSheet("""
            QAbstractItemView {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                selection-background-color: #3b82f6;
                selection-color: #ffffff;
            }
        """)
        self.setCompleter(completer)
