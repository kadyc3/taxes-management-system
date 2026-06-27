from __future__ import annotations
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QLineEdit, QComboBox, QLabel, QTextEdit,
)
from GUI.dialogs.base_dialog import BaseDialog
from GUI.widgets.base_widgets import FieldLabel, PrimaryButton, SecondaryButton
from Kernel.models.declaration import Declaration, DeclarationStatus, DeclarationType


class DeclarationDialog(BaseDialog):
    def __init__(
        self,
        declaration: Optional[Declaration] = None,
        taxpayer_names: Optional[list[str]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        is_edit = declaration is not None
        super().__init__(
            title="Edit Declaration" if is_edit else "New Declaration",
            subtitle="Update declaration details." if is_edit else "Create a new tax declaration.",
            parent=parent,
            min_width=540,
        )
        self._declaration = declaration or Declaration.empty()
        self._taxpayer_names = taxpayer_names or []
        self._build_form()

    def _build_form(self) -> None:
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # Taxpayer
        grid.addWidget(FieldLabel("Taxpayer *"), 0, 0)
        self._taxpayer = QComboBox()
        for name in self._taxpayer_names:
            self._taxpayer.addItem(name)
        idx = self._taxpayer.findText(self._declaration.taxpayer)
        if idx >= 0:
            self._taxpayer.setCurrentIndex(idx)
        elif self._declaration.taxpayer:
            self._taxpayer.addItem(self._declaration.taxpayer)
            self._taxpayer.setCurrentText(self._declaration.taxpayer)
        grid.addWidget(self._taxpayer, 1, 0)

        # Type
        grid.addWidget(FieldLabel("Declaration Type"), 0, 1)
        self._type = QComboBox()
        for t in DeclarationType:
            self._type.addItem(t.value)
        idx = self._type.findText(self._declaration.declaration_type.value)
        if idx >= 0:
            self._type.setCurrentIndex(idx)
        grid.addWidget(self._type, 1, 1)

        # Amount
        grid.addWidget(FieldLabel("Amount (TND) *"), 2, 0)
        self._amount = QLineEdit(str(self._declaration.amount))
        self._amount.setPlaceholderText("0.00")
        grid.addWidget(self._amount, 3, 0)

        # Date
        grid.addWidget(FieldLabel("Declaration Date"), 2, 1)
        self._date = QLineEdit(self._declaration.date)
        self._date.setPlaceholderText("YYYY-MM-DD")
        grid.addWidget(self._date, 3, 1)

        # Status
        grid.addWidget(FieldLabel("Status"), 4, 0)
        self._status = QComboBox()
        for s in DeclarationStatus:
            self._status.addItem(s.value)
        idx = self._status.findText(self._declaration.status.value)
        if idx >= 0:
            self._status.setCurrentIndex(idx)
        grid.addWidget(self._status, 5, 0)

        # Notes
        grid.addWidget(FieldLabel("Notes"), 4, 1)
        self._notes = QLineEdit(self._declaration.notes)
        self._notes.setPlaceholderText("Optional notes…")
        grid.addWidget(self._notes, 5, 1)

        self.add_content_layout(grid)

        self._error_lbl = QLabel("")
        self._error_lbl.setStyleSheet("color: #dc2626; font-size: 12px;")
        self._error_lbl.hide()
        self.add_content_widget(self._error_lbl)

        cancel_btn = SecondaryButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_btn = PrimaryButton("Save Declaration")
        save_btn.clicked.connect(self._on_save)
        self.add_button_row(cancel_btn, save_btn)

    def _on_save(self) -> None:
        taxpayer = self._taxpayer.currentText().strip()
        if not taxpayer:
            self._error_lbl.setText("Taxpayer is required.")
            self._error_lbl.show()
            return
        try:
            amount = float(self._amount.text().strip())
        except ValueError:
            self._error_lbl.setText("Amount must be a valid number.")
            self._error_lbl.show()
            return
        self._declaration.taxpayer = taxpayer
        self._declaration.declaration_type = DeclarationType(self._type.currentText())
        self._declaration.amount = amount
        self._declaration.date = self._date.text().strip()
        self._declaration.status = DeclarationStatus(self._status.currentText())
        self._declaration.notes = self._notes.text().strip()
        self.accept()

    def get_declaration(self) -> Declaration:
        return self._declaration