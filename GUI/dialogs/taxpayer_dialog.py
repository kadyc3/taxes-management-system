from __future__ import annotations
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QComboBox, QLabel, QGridLayout,
)
from PyQt6.QtCore import Qt

from GUI.dialogs.base_dialog import BaseDialog
from GUI.widgets.base_widgets import FieldLabel, PrimaryButton, SecondaryButton
from Kernel.models.taxpayer import Taxpayer, TaxpayerStatus, TaxpayerType


class TaxpayerDialog(BaseDialog):
    def __init__(
        self,
        taxpayer: Optional[Taxpayer] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        is_edit = taxpayer is not None
        super().__init__(
            title="Edit Taxpayer" if is_edit else "Add Taxpayer",
            subtitle="Update taxpayer details." if is_edit else "Register a new taxpayer profile.",
            parent=parent,
            min_width=520,
        )
        self._taxpayer = taxpayer or Taxpayer.empty()
        self._build_form()

    def _build_form(self) -> None:
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # Name
        grid.addWidget(FieldLabel("Full Name *"), 0, 0)
        self._name = QLineEdit(self._taxpayer.name)
        self._name.setPlaceholderText("e.g. TechNova Tunisie")
        grid.addWidget(self._name, 1, 0)

        # ID (read-only if editing)
        grid.addWidget(FieldLabel("Taxpayer ID"), 0, 1)
        self._id = QLineEdit(self._taxpayer.id)
        self._id.setPlaceholderText("Auto-generated")
        if self._taxpayer.id:
            self._id.setReadOnly(True)
            self._id.setStyleSheet("background-color: #f3f4f6; color: #9ca3af;")
        grid.addWidget(self._id, 1, 1)

        # Email
        grid.addWidget(FieldLabel("Email Address *"), 2, 0)
        self._email = QLineEdit(self._taxpayer.email)
        self._email.setPlaceholderText("contact@company.tn")
        grid.addWidget(self._email, 3, 0)

        # Phone
        grid.addWidget(FieldLabel("Phone"), 2, 1)
        self._phone = QLineEdit(self._taxpayer.phone)
        self._phone.setPlaceholderText("+216 XX XXX XXX")
        grid.addWidget(self._phone, 3, 1)

        # Status
        grid.addWidget(FieldLabel("Status"), 4, 0)
        self._status = QComboBox()
        for s in TaxpayerStatus:
            self._status.addItem(s.value)
        idx = self._status.findText(self._taxpayer.status.value)
        if idx >= 0:
            self._status.setCurrentIndex(idx)
        grid.addWidget(self._status, 5, 0)

        # Type
        grid.addWidget(FieldLabel("Taxpayer Type"), 4, 1)
        self._type = QComboBox()
        for t in TaxpayerType:
            self._type.addItem(t.value)
        idx = self._type.findText(self._taxpayer.taxpayer_type.value)
        if idx >= 0:
            self._type.setCurrentIndex(idx)
        grid.addWidget(self._type, 5, 1)

        # Registration Date
        grid.addWidget(FieldLabel("Registration Date"), 6, 0)
        self._reg_date = QLineEdit(self._taxpayer.registration_date)
        self._reg_date.setPlaceholderText("YYYY-MM-DD")
        grid.addWidget(self._reg_date, 7, 0)

        # Address
        grid.addWidget(FieldLabel("Address"), 6, 1)
        self._address = QLineEdit(self._taxpayer.address)
        self._address.setPlaceholderText("City, Region")
        grid.addWidget(self._address, 7, 1)

        self.add_content_layout(grid)

        # Error label
        self._error_lbl = QLabel("")
        self._error_lbl.setStyleSheet("color: #dc2626; font-size: 12px;")
        self._error_lbl.hide()
        self.add_content_widget(self._error_lbl)

        # Buttons
        cancel_btn = SecondaryButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = PrimaryButton("Save Taxpayer" if self._taxpayer.id else "Add Taxpayer")
        save_btn.clicked.connect(self._on_save)
        self.add_button_row(cancel_btn, save_btn)

    def _on_save(self) -> None:
        name = self._name.text().strip()
        email = self._email.text().strip()
        if not name or not email:
            self._error_lbl.setText("Name and email are required.")
            self._error_lbl.show()
            return
        self._taxpayer.name = name
        self._taxpayer.email = email
        self._taxpayer.phone = self._phone.text().strip()
        self._taxpayer.status = TaxpayerStatus(self._status.currentText())
        self._taxpayer.taxpayer_type = TaxpayerType(self._type.currentText())
        self._taxpayer.registration_date = self._reg_date.text().strip()
        self._taxpayer.address = self._address.text().strip()
        self.accept()

    def get_taxpayer(self) -> Taxpayer:
        return self._taxpayer