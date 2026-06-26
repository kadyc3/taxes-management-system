from PyQt6.QtWidgets import QTableWidget, QAbstractItemView

class StyledTable(QTableWidget):
    def __init__(self, columns):
        super().__init__()

        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels([c[0] for c in columns])

        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)