"""
GUI/pages/declaration_page.py

Full CRUD interface for tax declaration management.
Lives inside the DashboardWindow's QStackedWidget.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QDialogButtonBox, QDoubleSpinBox,
    QSpinBox, QAbstractItemView, QInputDialog,
)
from PyQt6.QtCore import Qt

from Kernel.models.declaration import Declaration
from Kernel.services.declaration_service import DeclarationService
from Kernel.services.taxpayer_service import TaxpayerService
from Kernel.services.auth_service import AuthService
from Kernel.exceptions.app_exceptions import AppError
from GUI.widgets.search_bar import SearchBar
from GUI.widgets.message_bar import MessageBar
from GUI.widgets.confirm_dialog import confirm


_TAX_TYPES = ["TVA", "IS", "IRPP", "RS", "TCL", "TFP", "FOPROLOS"]
_STATUSES = ["draft", "submitted", "validated", "rejected"]

_COLUMNS = [
    ("ID",          "id",            50),
    ("Reference",   "reference",    170),
    ("Taxpayer",    "taxpayer_name", 200),
    ("Tax Type",    "tax_rate",       80),
    ("Period",      "period", 100),
    ("Year",        "fiscal_year",    60),
    ("Total Due",   "total_due",     110),
    ("Status",      "status",         90),
]


class DeclarationPage(QWidget):
    def __init__(
        self,
        declaration_service: DeclarationService,
        taxpayer_service: TaxpayerService,
        auth_service: AuthService,
    ) -> None:
        super().__init__()
        self._svc = declaration_service
        self._tp_svc = taxpayer_service
        self._auth = auth_service
        self._build_ui()
        self.load_data()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Header
        header_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        page_title = QLabel("Declarations")
        page_title.setObjectName("PageTitle")
        page_subtitle = QLabel("Manage tax declarations for all taxpayers")
        page_subtitle.setObjectName("PageSubtitle")
        title_col.addWidget(page_title)
        title_col.addWidget(page_subtitle)
        header_row.addLayout(title_col)
        header_row.addStretch()

        self._add_btn = QPushButton("＋  New Declaration")
        self._add_btn.setMinimumHeight(36)
        self._add_btn.setFixedWidth(160)
        self._add_btn.clicked.connect(self._open_add_dialog)
        header_row.addWidget(self._add_btn)
        layout.addLayout(header_row)

        self._msg = MessageBar()
        layout.addWidget(self._msg)

        # Search
        self._search = SearchBar("Search by reference, taxpayer name, tax type…")
        self._search.search_triggered.connect(self._on_search)
        layout.addWidget(self._search)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(len(_COLUMNS))
        self._table.setHorizontalHeaderLabels([c[0] for c in _COLUMNS])
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setMinimumHeight(300)
        for i, (_, _, width) in enumerate(_COLUMNS):
            self._table.setColumnWidth(i, width)
        layout.addWidget(self._table, stretch=1)

        # Action buttons
        action_row = QHBoxLayout()
        action_row.setSpacing(8)

        self._edit_btn = QPushButton("✏  Edit")
        self._edit_btn.setObjectName("SecondaryButton")
        self._edit_btn.setMinimumHeight(34)
        self._edit_btn.setEnabled(False)
        self._edit_btn.clicked.connect(self._open_edit_dialog)

        self._submit_btn = QPushButton("▶  Submit")
        self._submit_btn.setObjectName("SecondaryButton")
        self._submit_btn.setMinimumHeight(34)
        self._submit_btn.setEnabled(False)
        self._submit_btn.clicked.connect(self._submit_selected)

        self._validate_btn = QPushButton("✔  Validate")
        self._validate_btn.setMinimumHeight(34)
        self._validate_btn.setEnabled(False)
        self._validate_btn.clicked.connect(self._validate_selected)

        self._reject_btn = QPushButton("✘  Reject")
        self._reject_btn.setObjectName("DangerButton")
        self._reject_btn.setMinimumHeight(34)
        self._reject_btn.setEnabled(False)
        self._reject_btn.clicked.connect(self._reject_selected)

        self._delete_btn = QPushButton("🗑  Delete")
        self._delete_btn.setObjectName("DangerButton")
        self._delete_btn.setMinimumHeight(34)
        self._delete_btn.setEnabled(False)
        self._delete_btn.clicked.connect(self._delete_selected)

        action_row.addStretch()
        for btn in (
            self._edit_btn, self._submit_btn,
            self._validate_btn, self._reject_btn,
            self._delete_btn,
        ):
            action_row.addWidget(btn)
        layout.addLayout(action_row)

        self._table.itemSelectionChanged.connect(self._on_selection_changed)

        # RBAC
        #user = self._auth.current_user
        #if user and not user.can_write():
         #   self._add_btn.setVisible(False)
        #if user and not user.is_admin():
         #   self._validate_btn.setVisible(False)
          #  self._reject_btn.setVisible(False)
           # self._delete_btn.setVisible(False)

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------
    def load_data(self, declarations: list[Declaration] | None = None) -> None:
        if declarations is None:
            try:
                declarations = self._svc.get_all()
            except AppError as exc:
                self._msg.show_error(str(exc))
                return

        self._table.setRowCount(0)
        for row_idx, decl in enumerate(declarations):
            self._table.insertRow(row_idx)
            values = [
                str(decl.id),
                f"DEC-{decl.id}",
                decl.taxpayer_name or str(decl.taxpayer_id),
                decl.tax_rate,
                decl.period,
                str(decl.fiscal_year),
                f"{decl.total_due:,.3f} TND",
                str(decl.status).capitalize(),
            ]
            for col_idx, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, decl.id)
                self._table.setItem(row_idx, col_idx, item)
        self._table.resizeRowsToContents()

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------
    def _on_selection_changed(self) -> None:
        has = bool(self._table.selectedItems())
        user = self._auth.current_user
        self._edit_btn.setEnabled(has and user.can_write())
        self._submit_btn.setEnabled(has and user.can_write())
        self._validate_btn.setEnabled(has and user.is_admin())
        self._reject_btn.setEnabled(has and user.is_admin())
        self._delete_btn.setEnabled(has and user.can_delete())


    def _selected_id(self) -> int | None:
        row = self._table.currentRow()
        if row < 0:
            return None

        item = self._table.item(row, 0)  # ID column
        if not item:
            return None

        return int(item.text())

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    def _on_search(self, query: str) -> None:
        try:
            results = self._svc.search(query)
            self.load_data(results)
        except AppError as exc:
            self._msg.show_error(str(exc))

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def _open_add_dialog(self) -> None:
        taxpayers = self._tp_svc.get_all()
        if not taxpayers:
            self._msg.show_error("No taxpayers found. Create a taxpayer first.")
            return
        dialog = DeclarationFormDialog(
            parent=self,
            service=self._svc,
            taxpayers=taxpayers,
            declaration=None,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self._msg.show_success("Declaration created successfully.")

    def _open_edit_dialog(self) -> None:
        decl_id = self._selected_id()
        if decl_id is None:
            self._msg.show_error("No declaration selected.")
            return

        try:
            declaration = self._svc.get_by_id(decl_id)
        except Exception as exc:
            self._msg.show_error(str(exc))
            return

        taxpayers = self._tp_svc.get_all()

        dialog = DeclarationFormDialog(
            parent=self,
            service=self._svc,
            taxpayers=taxpayers,
            declaration=declaration,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self._msg.show_success("Declaration updated successfully.")

    def _submit_selected(self) -> None:
        decl_id = self._selected_id()
        if decl_id is None:
            return
        try:
            self._svc.submit(decl_id, user_id=self._auth.current_user.id)
            self.load_data()
            self._msg.show_success("Declaration submitted.")
        except AppError as exc:
            self._msg.show_error(str(exc))

    def _validate_selected(self) -> None:
        decl_id = self._selected_id()
        if decl_id is None:
            return
        try:
            self._svc.validate_declaration(decl_id, user_id=self._auth.current_user.id)
            self.load_data()
            self._msg.show_success("Declaration validated.")
        except AppError as exc:
            self._msg.show_error(str(exc))

    def _reject_selected(self) -> None:
        decl_id = self._selected_id()
        if decl_id is None:
            return
        reason, ok = QInputDialog.getText(self, "Reject Declaration", "Rejection reason:")
        if not ok or not reason.strip():
            return
        try:
            self._svc.reject_declaration(decl_id, reason.strip(), user_id=self._auth.current_user.id)
            self.load_data()
            self._msg.show_success("Declaration rejected.")
        except AppError as exc:
            self._msg.show_error(str(exc))

    def _delete_selected(self) -> None:
        decl_id = self._selected_id()
        if decl_id is None:
            return
        if not confirm(self, "Delete Declaration", "Delete this declaration permanently?"):
            return
        try:
            self._svc.delete(decl_id, user_id=self._auth.current_user.id)
            self.load_data()
            self._msg.show_success("Declaration deleted.")
        except AppError as exc:
            self._msg.show_error(str(exc))


# ======================================================================
# Declaration Form Dialog
# ======================================================================

class DeclarationFormDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        service: DeclarationService,
        taxpayers,
        declaration: Declaration | None,
    ) -> None:
        super().__init__(parent)
        self._svc = service
        self._taxpayers = taxpayers
        self._declaration = declaration
        self._is_edit = declaration is not None
        self.setWindowTitle("Edit Declaration" if self._is_edit else "New Declaration")
        self.setModal(True)
        self.setMinimumWidth(480)
        self._build_ui()
        if self._is_edit:
            self._populate()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self._msg = MessageBar()
        layout.addWidget(self._msg)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setSpacing(10)

        # Taxpayer dropdown
        self._taxpayer_combo = QComboBox()
        for tp in self._taxpayers:
            self._taxpayer_combo.addItem(f"{tp.name} ({tp.tax_id})", userData=tp.id)

        self._tax_type_combo = QComboBox()
        self._tax_type_combo.addItems(_TAX_TYPES)

        self._fiscal_year_spin = QSpinBox()
        self._fiscal_year_spin.setRange(1990, 2100)
        self._fiscal_year_spin.setValue(2024)

        self._fiscal_period_input = QLineEdit()
        self._fiscal_period_input.setPlaceholderText("e.g. T1-2024, M03-2024, 2024")

        self._gross_spin = QDoubleSpinBox()
        self._gross_spin.setRange(0, 999_999_999)
        self._gross_spin.setDecimals(3)
        self._gross_spin.setSuffix(" TND")
        self._gross_spin.valueChanged.connect(self._recompute)

        self._deductions_spin = QDoubleSpinBox()
        self._deductions_spin.setRange(0, 999_999_999)
        self._deductions_spin.setDecimals(3)
        self._deductions_spin.setSuffix(" TND")
        self._deductions_spin.valueChanged.connect(self._recompute)

        self._penalties_spin = QDoubleSpinBox()
        self._penalties_spin.setRange(0, 999_999_999)
        self._penalties_spin.setDecimals(3)
        self._penalties_spin.setSuffix(" TND")
        self._penalties_spin.valueChanged.connect(self._recompute)

        self._total_due_label = QLabel("0.000 TND")
        self._total_due_label.setStyleSheet("font-weight: bold; color: #8B0000;")

        self._status_combo = QComboBox()
        self._status_combo.addItems(_STATUSES)

        self._notes_input = QTextEdit()
        self._notes_input.setMaximumHeight(60)
        self._notes_input.setPlaceholderText("Optional notes…")

        form.addRow("Taxpayer *", self._taxpayer_combo)
        form.addRow("Tax Type *", self._tax_type_combo)
        form.addRow("Fiscal Year *", self._fiscal_year_spin)
        form.addRow("Fiscal Period *", self._fiscal_period_input)
        form.addRow("Gross Amount", self._gross_spin)
        form.addRow("Deductions", self._deductions_spin)
        form.addRow("Penalties", self._penalties_spin)
        form.addRow("Total Due", self._total_due_label)
        form.addRow("Status", self._status_combo)
        form.addRow("Notes", self._notes_input)
        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate(self) -> None:
        decl = self._declaration
        for i in range(self._taxpayer_combo.count()):
            if self._taxpayer_combo.itemData(i) == decl.taxpayer_id:
                self._taxpayer_combo.setCurrentIndex(i)
                break
        idx = self._tax_type_combo.findText(decl.tax_rate)
        if idx >= 0:
            self._tax_type_combo.setCurrentIndex(idx)
        self._fiscal_year_spin.setValue(decl.fiscal_year)
        self._fiscal_period_input.setText(decl.period)
        self._gross_spin.setValue(decl.gross_amount)
        self._penalties_spin.setValue(decl.penalties)
        idx = self._status_combo.findText(decl.status)
        if idx >= 0:
            self._status_combo.setCurrentIndex(idx)
        self._notes_input.setPlainText(decl.notes or "")
        self._recompute()

    def _recompute(self) -> None:
        gross = self._gross_spin.value()
        ded = self._deductions_spin.value()
        pen = self._penalties_spin.value()
        total = (gross - ded) + pen
        self._total_due_label.setText(f"{total:,.3f} TND")

    def _save(self) -> None:
        self._msg.hide()
        data = {
        "id": self._declaration.id if self._is_edit else None,
        "taxpayer_id": self._taxpayer_combo.currentData(),
        "declaration_type": self._tax_type_combo.currentText(),
        "fiscal_year": self._fiscal_year_spin.value(),
        "period": self._fiscal_period_input.text(),
        "gross_amount": self._gross_spin.value(),
        "tax_rate": self._gross_spin.value(),
        "penalties": self._penalties_spin.value(),
        "status": self._status_combo.currentText(),
        "notes": self._notes_input.toPlainText(),
    }
        try:
            if self._is_edit:
                self._svc.update(self._declaration.id, data)
            else:
                self._svc.create(data)
            self.accept()
        except AppError as exc:
            self._msg.show_error(str(exc))