from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QTextEdit
)

from Kernel.models.taxpayer import Taxpayer, TaxpayerType, TaxpayerStatus


class TaxpayerFormDialog(QDialog):

    def __init__(self, service, taxpayer=None):
        super().__init__()

        self.service = service
        self.taxpayer = taxpayer
        self.is_edit = taxpayer is not None

        self.setWindowTitle("Edit Taxpayer" if self.is_edit else "Add Taxpayer")
        self.setMinimumWidth(420)

        self._build_ui()

        if self.is_edit:
            self._fill()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.name = QLineEdit()
        self.tax_id = QLineEdit()
        self.email = QLineEdit()
        self.phone = QLineEdit()
        self.address = QTextEdit()
        self.address.setMaximumHeight(70)

        self.type = QComboBox()
        self.type.addItems([t.value for t in TaxpayerType])

        self.status = QComboBox()
        self.status.addItems([s.value for s in TaxpayerStatus])

        form.addRow("Name", self.name)
        form.addRow("Tax ID", self.tax_id)
        form.addRow("Email", self.email)
        form.addRow("Phone", self.phone)
        form.addRow("Address", self.address)
        form.addRow("Type", self.type)
        form.addRow("Status", self.status)

        layout.addLayout(form)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save)
        layout.addWidget(self.save_btn)

    def _fill(self):
        t = self.taxpayer
        self.name.setText(t.name)
        self.tax_id.setText(t.tax_id)
        self.email.setText(t.email or "")
        self.phone.setText(t.phone or "")
        self.address.setPlainText(t.address or "")

    def save(self):
        data = {
            "name": self.name.text().strip(),
            "tax_id": self.tax_id.text().strip(),
            "email": self.email.text().strip(),
            "phone": self.phone.text().strip(),
            "address": self.address.toPlainText().strip(),
            "type": self.type.currentText(),
            "status": self.status.currentText(),
        }

        if self.is_edit:
            self.service.update(self.taxpayer.id, data)
        else:
            self.service.create(data)

        self.accept()