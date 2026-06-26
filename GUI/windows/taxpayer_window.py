"""
GUI/windows/taxpayer_window.py

Full CRUD interface for taxpayer management.
Lives inside the DashboardWindow's QStackedWidget.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton,
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QDialogButtonBox, QHeaderView,
    QAbstractItemView, QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from Kernel.models.taxpayer import Taxpayer
from Kernel.services.taxpayer_service import TaxpayerService
from Kernel.services.auth_service import AuthService
from Kernel.exceptions.app_exceptions import AppError
from GUI.widgets.search_bar import SearchBar
from GUI.widgets.message_bar import MessageBar
from GUI.widgets.confirm_dialog import confirm


# Column definitions: (header_label, attribute_name, width)
_COLUMNS = [
    ("ID",              "id",               50),
    ("Matricule Fiscal","tax_id",           130),
    ("Name",            "name",             220),
    ("Type",            "display_type",     110),
    ("City",            "city",             110),
    ("Status",          "status",           90),
    ("Registered",      "registration_date",100),
]


class TaxpayerWindow(QWidget):
    def __init__(
        self,
        taxpayer_service: TaxpayerService,
        auth_service: AuthService,
    ) -> None:
        super().__init__()
        self._svc = taxpayer_service
        self._auth = auth_service
        self._build_ui()
        self.load_data()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        # --- Header ---
        header_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        page_title = QLabel("Taxpayers")
        page_title.setObjectName("PageTitle")
        page_subtitle = QLabel("Manage Tunisian economic entities")
        page_subtitle.setObjectName("PageSubtitle")
        title_col.addWidget(page_title)
        title_col.addWidget(page_subtitle)
        header_row.addLayout(title_col)
        header_row.addStretch()

        self._add_btn = QPushButton("＋  Add Taxpayer")
        self._add_btn.setObjectName("PrimaryButton")
        self._add_btn.setMinimumHeight(36)
        self._add_btn.setFixedWidth(150)
        self._add_btn.clicked.connect(self._open_add_dialog)
        header_row.addWidget(self._add_btn)
        layout.addLayout(header_row)

        # --- Message bar ---
        self._msg = MessageBar()
        layout.addWidget(self._msg)

        # --- Search ---
        self._search = SearchBar("Search by name, matricule, city…")
        self._search.search_triggered.connect(self._on_search)
        layout.addWidget(self._search)

        # --- Table ---
        self._table = QTableWidget()
        self._table.setColumnCount(len(_COLUMNS))
        self._table.setHorizontalHeaderLabels([c[0] for c in _COLUMNS])
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.setStyleSheet("""
        QTableWidget {
            background: white;
            border-radius: 8px;
            border: 1px solid #E5E7EB;
        }

        QTableWidget::item {
            padding: 8px;
        }

        QTableWidget::item:selected {
            background-color: #DBEAFE;
        }

        QHeaderView::section {
            background-color: #F3F4F6;
            padding: 8px;
            border: none;
            font-weight: 600;
        }
        """)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setMinimumHeight(300)

        for i, (_, _, width) in enumerate(_COLUMNS):
            self._table.setColumnWidth(i, width)

        layout.addWidget(self._table, stretch=1)

        # --- Action buttons ---
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self._edit_btn = QPushButton("✏  Edit")
        self._edit_btn.setObjectName("SecondaryButton")
        self._edit_btn.setMinimumHeight(34)
        self._edit_btn.setEnabled(False)
        self._edit_btn.clicked.connect(self._open_edit_dialog)

        self._delete_btn = QPushButton("🗑  Delete")
        self._delete_btn.setObjectName("DangerButton")
        self._delete_btn.setMinimumHeight(34)
        self._delete_btn.setEnabled(False)
        self._delete_btn.clicked.connect(self._delete_selected)

        action_row.addStretch()
        action_row.addWidget(self._edit_btn)
        action_row.addWidget(self._delete_btn)
        layout.addLayout(action_row)

        self._table.itemSelectionChanged.connect(self._on_selection_changed)

        # RBAC: hide write actions for viewers
        user = self._auth.current_user
        if user and not user.can_write():
            self._add_btn.setVisible(False)
        if user and not user.can_delete():
            self._delete_btn.setVisible(False)

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    def load_data(self, taxpayers: list[Taxpayer] | None = None) -> None:
        if taxpayers is None:
            try:
                taxpayers = self._svc.get_all()
            except AppError as exc:
                self._msg.show_error(str(exc))
                return

        self._table.setRowCount(0)
        for row_idx, tp in enumerate(taxpayers):
            self._table.insertRow(row_idx)
            values = [
                str(tp.id),
                tp.tax_id,
                tp.name,
                tp.display_type(),
                tp.city or "—",
                tp.status.capitalize(),
                tp.registration_date or "—",
            ]
            for col_idx, val in enumerate(values):
                item = QTableWidgetItem(val)
                item.setData(Qt.ItemDataRole.UserRole, tp.id)
                self._table.setItem(row_idx, col_idx, item)

        self._table.resizeRowsToContents()

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------
    def _on_selection_changed(self) -> None:
        has_selection = bool(self._table.selectedItems())
        user = self._auth.current_user
        self._edit_btn.setEnabled(has_selection and user.can_write())
        self._delete_btn.setEnabled(has_selection and user.can_delete())

    def _selected_taxpayer_id(self) -> int | None:
        rows = self._table.selectedItems()
        if not rows:
            return None
        return rows[0].data(Qt.ItemDataRole.UserRole)

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
    # CRUD dialogs
    # ------------------------------------------------------------------
    def _open_add_dialog(self) -> None:
        dialog = TaxpayerFormDialog(
            parent=self,
            service=self._svc,
            taxpayer=None,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self._msg.show_success("Taxpayer created successfully.")

    def _open_edit_dialog(self) -> None:
        tp_id = self._selected_taxpayer_id()
        if tp_id is None:
            return
        try:
            taxpayer = self._svc.get_by_id(tp_id)
        except AppError as exc:
            self._msg.show_error(str(exc))
            return

        dialog = TaxpayerFormDialog(
            parent=self,
            service=self._svc,
            taxpayer=taxpayer,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
            self._msg.show_success("Taxpayer updated successfully.")

    def _delete_selected(self) -> None:
        tp_id = self._selected_taxpayer_id()
        if tp_id is None:
            return
        if not confirm(
            self,
            "Delete Taxpayer",
            "This will permanently delete the taxpayer and all their declarations.\n"
            "This action cannot be undone. Proceed?",
        ):
            return
        try:
            self._svc.delete(tp_id)
            self.load_data()
            self._msg.show_success("Taxpayer deleted.")
        except AppError as exc:
            self._msg.show_error(str(exc))


# ======================================================================
# Taxpayer Form Dialog (Add / Edit)
# ======================================================================

class TaxpayerFormDialog(QDialog):
    def __init__(
        self,
        parent: QWidget,
        service: TaxpayerService,
        taxpayer: Taxpayer | None,
    ) -> None:
        super().__init__(parent)
        self._svc = service
        self._taxpayer = taxpayer
        self._is_edit = taxpayer is not None
        self.setWindowTitle("Edit Taxpayer" if self._is_edit else "Add Taxpayer")
        self.setModal(True)
        self.setMinimumWidth(500)
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

        self._tax_id_input = QLineEdit()
        self._tax_id_input.setPlaceholderText("e.g. 1234567A/P/M/000")

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("Legal or full name")

        self._type_combo = QComboBox()
        self._type_combo.addItems(["legal", "physical"])

        self._legal_form_input = QLineEdit()
        self._legal_form_input.setPlaceholderText("SARL, SA, EI, SUARL…")

        self._address_input = QLineEdit()
        self._city_input = QLineEdit()
        self._postal_input = QLineEdit()
        self._phone_input = QLineEdit()
        self._email_input = QLineEdit()
        self._sector_input = QLineEdit()
        self._reg_date_input = QLineEdit()
        self._reg_date_input.setPlaceholderText("YYYY-MM-DD")

        self._status_combo = QComboBox()
        self._status_combo.addItems(["active", "suspended", "deregistered"])

        self._notes_input = QTextEdit()
        self._notes_input.setMaximumHeight(70)
        self._notes_input.setPlaceholderText("Optional notes…")

        form.addRow("Matricule Fiscal *", self._tax_id_input)
        form.addRow("Name *", self._name_input)
        form.addRow("Type *", self._type_combo)
        form.addRow("Legal Form", self._legal_form_input)
        form.addRow("Address", self._address_input)
        form.addRow("City", self._city_input)
        form.addRow("Postal Code", self._postal_input)
        form.addRow("Phone", self._phone_input)
        form.addRow("Email", self._email_input)
        form.addRow("Activity Sector", self._sector_input)
        form.addRow("Registration Date", self._reg_date_input)
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
        tp = self._taxpayer
        self._tax_id_input.setText(tp.tax_id)
        self._name_input.setText(tp.name)
        idx = self._type_combo.findText(tp.taxpayer_type)
        if idx >= 0:
            self._type_combo.setCurrentIndex(idx)
        self._legal_form_input.setText(tp.legal_form or "")
        self._address_input.setText(tp.address or "")
        self._city_input.setText(tp.city or "")
        self._postal_input.setText(tp.postal_code or "")
        self._phone_input.setText(tp.phone or "")
        self._email_input.setText(tp.email or "")
        self._sector_input.setText(tp.activity_sector or "")
        self._reg_date_input.setText(tp.registration_date or "")
        idx = self._status_combo.findText(tp.status)
        if idx >= 0:
            self._status_combo.setCurrentIndex(idx)
        self._notes_input.setPlainText(tp.notes or "")

    def _save(self) -> None:
        self._msg.hide()
        data = {
            "tax_id": self._tax_id_input.text(),
            "name": self._name_input.text(),
            "taxpayer_type": self._type_combo.currentText(),
            "legal_form": self._legal_form_input.text(),
            "address": self._address_input.text(),
            "city": self._city_input.text(),
            "postal_code": self._postal_input.text(),
            "phone": self._phone_input.text(),
            "email": self._email_input.text(),
            "activity_sector": self._sector_input.text(),
            "registration_date": self._reg_date_input.text(),
            "status": self._status_combo.currentText(),
            "notes": self._notes_input.toPlainText(),
        }
        try:
            if self._is_edit:
                self._svc.update(self._taxpayer.id, data)
            else:
                self._svc.create(data)
            self.accept()
        except AppError as exc:
            self._msg.show_error(str(exc))