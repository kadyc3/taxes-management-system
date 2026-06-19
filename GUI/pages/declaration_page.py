from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel
)


class DeclarationPage(QWidget):
    def __init__(self, declaration_service):
        super().__init__()
        self.service = declaration_service
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Declarations")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Refresh button
        btn_row = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        btn_row.addWidget(refresh_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Taxpayer", "Type", "Amount", "Status", "Date"
        ])

        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        declarations = self.service.get_all()

        self.table.setRowCount(len(declarations))

        for i, d in enumerate(declarations):
            self.table.setItem(i, 0, QTableWidgetItem(str(d.id)))
            self.table.setItem(i, 1, QTableWidgetItem(str(d.taxpayer_id)))
            self.table.setItem(i, 2, QTableWidgetItem(str(d.type)))
            self.table.setItem(i, 3, QTableWidgetItem(str(d.amount)))
            self.table.setItem(i, 4, QTableWidgetItem(str(d.status)))
            self.table.setItem(i, 5, QTableWidgetItem(str(d.created_at)))