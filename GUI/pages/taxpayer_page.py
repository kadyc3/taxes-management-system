from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QAbstractItemView,
    QLineEdit, QMessageBox, QHeaderView, QSizePolicy
)
from PyQt6.QtCore import Qt

from GUI.dialogs.taxpayer_dialog import TaxpayerFormDialog
from Kernel.models.taxpayer import Taxpayer


class TaxpayerPage(QWidget):
    def __init__(self, taxpayer_service):
        super().__init__()
        self.service = taxpayer_service

        self.columns = ["ID", "Name", "Tax ID", "Email", "Phone", "Address"]

        self._build_ui()
        self.load_data()

    # ---------------- UI ----------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ---------- Search ----------
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or tax ID...")
        self.search_input.textChanged.connect(self._search_taxpayer)
        layout.addWidget(self.search_input)

        # ---------- Buttons ----------
        btn_row = QHBoxLayout()

        self.add_btn = QPushButton("＋ Add")
        self.add_btn.clicked.connect(self._add_taxpayer)

        self.edit_btn = QPushButton("✏ Edit")
        self.edit_btn.clicked.connect(self._edit_taxpayer)

        self.delete_btn = QPushButton("🗑 Delete")
        self.delete_btn.clicked.connect(self._delete_taxpayer)

        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.edit_btn)
        btn_row.addWidget(self.delete_btn)

        layout.addLayout(btn_row)

        # ---------- TABLE ----------
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)

        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setWordWrap(False)

        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # header behavior (important for SaaS look)
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(420)

        self.table.setStyleSheet("""
        QTableWidget {
            background: white;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
        }

        QTableWidget::item {
            padding: 10px;
            border-bottom: 1px solid #F3F4F6;
        }

        QTableWidget::item:selected {
            background-color: #DBEAFE;
        }

        QHeaderView::section {
            background-color: #F9FAFB;
            padding: 8px;
            border: none;
            font-weight: 600;
        }
        """)

        layout.addWidget(self.table)

    # ---------------- LOAD ----------------
    def load_data(self):
        taxpayers = self.service.get_all()

        self.table.setRowCount(0)

        for i, t in enumerate(taxpayers):
            self.table.insertRow(i)

            self.table.setItem(i, 0, QTableWidgetItem(str(t.id)))
            self.table.setItem(i, 1, QTableWidgetItem(t.name))
            self.table.setItem(i, 2, QTableWidgetItem(t.tax_id))
            self.table.setItem(i, 3, QTableWidgetItem(t.email or "—"))
            self.table.setItem(i, 4, QTableWidgetItem(t.phone or "—"))
            self.table.setItem(i, 5, QTableWidgetItem(t.address or "—"))

    # ---------------- SEARCH ----------------
    def _search_taxpayer(self, text):
        if not text:
            self.load_data()
            return

        results = self.service.search(text)

        self.table.setRowCount(0)

        for i, t in enumerate(results):
            self.table.insertRow(i)

            self.table.setItem(i, 0, QTableWidgetItem(str(t.id)))
            self.table.setItem(i, 1, QTableWidgetItem(t.name))
            self.table.setItem(i, 2, QTableWidgetItem(t.tax_id))
            self.table.setItem(i, 3, QTableWidgetItem(t.email or "—"))
            self.table.setItem(i, 4, QTableWidgetItem(t.phone or "—"))
            self.table.setItem(i, 5, QTableWidgetItem(t.address or "—"))

    # ---------------- ADD ----------------
    def _add_taxpayer(self):
        dialog = TaxpayerFormDialog(self.service)
        if dialog.exec():
            self.load_data()

    # ---------------- EDIT ----------------
    def _edit_taxpayer(self):
        row = self.table.currentRow()
        if row < 0:
            return

        taxpayer_id = int(self.table.item(row, 0).text())
        taxpayer = self.service.get_by_id(taxpayer_id)

        dialog = TaxpayerFormDialog(self.service, taxpayer)
        if dialog.exec():
            self.load_data()

    # ---------------- DELETE ----------------
    def _delete_taxpayer(self):
        row = self.table.currentRow()
        if row < 0:
            return

        taxpayer_id = int(self.table.item(row, 0).text())

        confirm = QMessageBox.question(
            self,
            "Delete",
            "Are you sure you want to delete this taxpayer?"
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.service.delete(taxpayer_id)
            self.load_data()