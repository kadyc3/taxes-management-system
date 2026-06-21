from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
from Kernel.models.taxpayer import Taxpayer, TaxpayerType, TaxpayerStatus
from PyQt6.QtWidgets import QLineEdit
from datetime import datetime

class TaxpayerPage(QWidget):
    def __init__(self, taxpayer_service):
        super().__init__()
        self.service = taxpayer_service
        self._build_ui()
        self.load_data()

    def _build_ui(self):
        layout = QVBoxLayout()

        # TABLE
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # BUTTON
        self.add_btn = QPushButton("Add Taxpayer")
        self.add_btn.clicked.connect(self._add_taxpayer)
        layout.addWidget(self.add_btn)

        #delete
        self.delete_btn = QPushButton("Delete Taxpayer")
        self.delete_btn.clicked.connect(self._delete_taxpayer)
        layout.addWidget(self.delete_btn)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or tax ID...")
        self.search_input.textChanged.connect(self._search_taxpayer)
        layout.addWidget(self.search_input)

        self.edit_btn = QPushButton("Edit Taxpayer")
        self.edit_btn.clicked.connect(self._edit_taxpayer)
        layout.addWidget(self.edit_btn)

        self.setLayout(layout)

        
    def _add_taxpayer(self):
        import uuid

        new_taxpayer = Taxpayer(
            tax_id=f"TAX{str(uuid.uuid4())[:8].upper()}",
            name=f"User {datetime.now().strftime('%H%M%S')}",
            taxpayer_type=TaxpayerType.PHYSICAL,
            status=TaxpayerStatus.ACTIVE,
            email="test@test.com",
            phone="123456",
            address="Tunis"
        )

        self.service.create(new_taxpayer)
        self.load_data()

    def _delete_taxpayer(self):
        row = self.table.currentRow()

        if row < 0:
            print("No taxpayer selected")
            return

        taxpayer_id = int(self.table.item(row, 0).text())

        self.service.delete(taxpayer_id)

        self.load_data()

    def _search_taxpayer(self, text):
        if not text:
            self.load_data()
            return

        results = self.service.search(text)

        self.table.setRowCount(len(results))
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Tax ID"])

        for i, t in enumerate(results):
            self.table.setItem(i, 0, QTableWidgetItem(str(t.id)))
            self.table.setItem(i, 1, QTableWidgetItem(t.name))
            self.table.setItem(i, 2, QTableWidgetItem(t.tax_id))
    
    def _edit_taxpayer(self):
        row = self.table.currentRow()

        if row < 0:
            print("No taxpayer selected")
            return

        taxpayer_id = int(self.table.item(row, 0).text())

        # get existing taxpayer
        taxpayer = self.service.get_by_id(taxpayer_id)

        # simple update (for now hardcoded test)
        taxpayer.name = taxpayer.name + " (Updated)"

        self.service.update(taxpayer)

        self.load_data()

    def load_data(self):
        taxpayers = self.service.get_all()

        self.table.clear()  # IMPORTANT
        self.table.setRowCount(0)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Tax ID"])

        for i, t in enumerate(taxpayers):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(t.id)))
            self.table.setItem(i, 1, QTableWidgetItem(t.name))
            self.table.setItem(i, 2, QTableWidgetItem(t.tax_id))