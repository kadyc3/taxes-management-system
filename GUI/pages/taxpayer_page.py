from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem


class TaxpayerPage(QWidget):
    def __init__(self, taxpayer_service):
        super().__init__()
        self.service = taxpayer_service
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        layout = QVBoxLayout()

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        taxpayers = self.service.get_all()

        self.table.setRowCount(len(taxpayers))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Tax ID"])

        for i, t in enumerate(taxpayers):
            self.table.setItem(i, 0, QTableWidgetItem(str(t.id)))
            self.table.setItem(i, 1, QTableWidgetItem(t.name))
            self.table.setItem(i, 2, QTableWidgetItem(t.tax_id))
        print("Loading taxpayers...")
        print(self.service.get_all())