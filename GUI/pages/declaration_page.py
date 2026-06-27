from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QHeaderView, QFrame, QFileDialog, QDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from ..widgets.search_bar import SearchBar
from ..widgets.message_bar import MessageBar
from ..dialogs.declaration_dialog import DeclarationDialog
from ..dialogs.confirm_dialog import ConfirmDialog, RejectionDialog
from Kernel.models.user import UserRole
from Kernel.exceptions.app_exceptions import PermissionDeniedError, ValidationError

class DeclarationPage(QWidget):
    def __init__(self, declaration_service, taxpayer_service, current_user, parent=None):
        super().__init__(parent)
        self.declaration_service = declaration_service
        self.taxpayer_service = taxpayer_service
        self.current_user = current_user
        
        # Pagination state
        self.all_declarations = []
        self.current_page = 1
        self.page_size = 10

        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header area
        header_hbox = QHBoxLayout()
        title = QLabel("Declarations Registry", self)
        title.setObjectName("HeaderTitle")
        header_hbox.addWidget(title)

        self.message_bar = MessageBar(self)
        header_hbox.addWidget(self.message_bar, 1)
        layout.addLayout(header_hbox)

        # Toolbar Card Frame
        toolbar_frame = QFrame(self)
        toolbar_frame.setObjectName("CardFrame")
        toolbar_frame.setProperty("class", "CardFrame")
        toolbar_layout = QVBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(15, 12, 15, 12)
        toolbar_layout.setSpacing(10)

        # Top row: Search and Filter
        row_1 = QHBoxLayout()
        self.search_bar = SearchBar("Search reference, taxpayer, type...", toolbar_frame)
        self.search_bar.textChanged.connect(self.on_filter_changed)
        row_1.addWidget(self.search_bar, 2)

        self.status_filter = QComboBox(toolbar_frame)
        self.status_filter.addItems(["All Statuses", "Draft", "Submitted", "Validated", "Rejected"])
        self.status_filter.currentIndexChanged.connect(self.on_filter_changed)
        row_1.addWidget(self.status_filter, 1)
        
        row_1.addStretch(1)

        # Action Buttons
        self.excel_export_btn = QPushButton("Export Excel (.xlsx)", toolbar_frame)
        self.excel_export_btn.clicked.connect(self.on_export_excel)
        row_1.addWidget(self.excel_export_btn)

        self.csv_export_btn = QPushButton("Export CSV", toolbar_frame)
        self.csv_export_btn.clicked.connect(self.on_export_csv)
        row_1.addWidget(self.csv_export_btn)

        toolbar_layout.addLayout(row_1)

        # Bottom row: CRUD and Workflow Actions
        row_2 = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Declaration", toolbar_frame)
        self.add_btn.setObjectName("PrimaryButton")
        self.add_btn.clicked.connect(self.on_add_clicked)
        row_2.addWidget(self.add_btn)

        self.edit_btn = QPushButton("Edit", toolbar_frame)
        self.edit_btn.clicked.connect(self.on_edit_clicked)
        row_2.addWidget(self.edit_btn)

        self.submit_btn = QPushButton("Submit for Validation", toolbar_frame)
        self.submit_btn.clicked.connect(self.on_submit_clicked)
        row_2.addWidget(self.submit_btn)

        # Admin workflow separators
        self.validate_btn = QPushButton("Validate", toolbar_frame)
        self.validate_btn.setObjectName("SuccessButton")
        self.validate_btn.clicked.connect(self.on_validate_clicked)
        row_2.addWidget(self.validate_btn)

        self.reject_btn = QPushButton("Reject", toolbar_frame)
        self.reject_btn.setObjectName("WarningButton")
        self.reject_btn.clicked.connect(self.on_reject_clicked)
        row_2.addWidget(self.reject_btn)

        self.delete_btn = QPushButton("Delete", toolbar_frame)
        self.delete_btn.setObjectName("DangerButton")
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        row_2.addWidget(self.delete_btn)

        row_2.addStretch()
        toolbar_layout.addLayout(row_2)

        layout.addWidget(toolbar_frame)

        # Declarations Table
        self.table = QTableWidget(self)
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "Reference", "Taxpayer", "Type", "Year", "Period",
            "Gross", "Deductions", "Penalties", "Total Tax", "Status",
            "Filed Date", "Rejection Reason"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Taxpayer name stretches
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_edit_clicked)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.table)

        # Pagination controls
        pagination_layout = QHBoxLayout()
        pagination_layout.addStretch()

        self.prev_btn = QPushButton("◀ Prev", self)
        self.prev_btn.setFixedWidth(80)
        self.prev_btn.clicked.connect(self.on_prev_page)
        pagination_layout.addWidget(self.prev_btn)

        self.page_label = QLabel("Page 1 of 1", self)
        self.page_label.setStyleSheet("font-weight: bold; color: #94a3b8; padding: 0px 10px;")
        pagination_layout.addWidget(self.page_label)

        self.next_btn = QPushButton("Next ▶", self)
        self.next_btn.setFixedWidth(80)
        self.next_btn.clicked.connect(self.on_next_page)
        pagination_layout.addWidget(self.next_btn)

        pagination_layout.addStretch()
        layout.addLayout(pagination_layout)

        # Configure visibility
        self.apply_role_permissions()
        
        # Load Initial Data
        self.refresh_list()

    def apply_role_permissions(self):
        role = self.current_user.role
        if role == UserRole.ADMIN:
            self.add_btn.setVisible(True)
            self.edit_btn.setVisible(True)
            self.submit_btn.setVisible(True)
            self.validate_btn.setVisible(True)
            self.reject_btn.setVisible(True)
            self.delete_btn.setVisible(True)
        elif role == UserRole.EDITOR:
            self.add_btn.setVisible(True)
            self.edit_btn.setVisible(True)
            self.submit_btn.setVisible(True)
            self.validate_btn.setVisible(False)
            self.reject_btn.setVisible(False)
            self.delete_btn.setVisible(False)
        else: # USER
            self.add_btn.setVisible(False)
            self.edit_btn.setVisible(False)
            self.submit_btn.setVisible(False)
            self.validate_btn.setVisible(False)
            self.reject_btn.setVisible(False)
            self.delete_btn.setVisible(False)

    def refresh_list(self):
        # Fetch status filter value
        status_text = self.status_filter.currentText()
        status_val = None if status_text == "All Statuses" else status_text

        query = self.search_bar.text().strip()

        # Call service to find declarations
        try:
            self.all_declarations = self.declaration_service.search_declarations(query, status_val)
            
            # Setup Autocomplete suggestions list (References & Taxpayers & Types)
            autocomplete_terms = []
            for d in self.all_declarations:
                if d.reference_number not in autocomplete_terms:
                    autocomplete_terms.append(d.reference_number)
                if d.taxpayer_name and d.taxpayer_name not in autocomplete_terms:
                    autocomplete_terms.append(d.taxpayer_name)
                if d.declaration_type not in autocomplete_terms:
                    autocomplete_terms.append(d.declaration_type)
            self.search_bar.set_autocomplete_list(autocomplete_terms)

            # Reset page
            self.current_page = 1
            self.render_table_page()
            self.on_selection_changed() # Force action button updates
        except Exception as e:
            self.message_bar.show_message(f"Error fetching declarations: {str(e)}", "error")

    def render_table_page(self):
        total_items = len(self.all_declarations)
        total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)

        if self.current_page > total_pages:
            self.current_page = total_pages
        if self.current_page < 1:
            self.current_page = 1

        self.page_label.setText(f"Page {self.current_page} of {total_pages}")
        self.prev_btn.setEnabled(self.current_page > 1)
        self.next_btn.setEnabled(self.current_page < total_pages)

        # Slice data
        start_idx = (self.current_page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        page_items = self.all_declarations[start_idx:end_idx]

        self.table.setRowCount(0)
        
        for idx, d in enumerate(page_items):
            self.table.insertRow(idx)
            
            # Reference with database ID stored in userData
            ref_item = QTableWidgetItem(d.reference_number)
            ref_item.setData(Qt.ItemDataRole.UserRole, d.id)
            ref_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            yr_item = QTableWidgetItem(str(d.fiscal_year))
            yr_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            per_item = QTableWidgetItem(d.period)
            per_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Currency Formats
            gross_item = QTableWidgetItem(f"$ {d.gross_amount:,.2f}")
            gross_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            ded_item = QTableWidgetItem(f"$ {d.deductions:,.2f}")
            ded_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            pen_item = QTableWidgetItem(f"$ {d.penalties:,.2f}")
            pen_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            due_item = QTableWidgetItem(f"$ {d.total_due:,.2f}")
            due_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            due_item_font = due_item.font()
            due_item_font.setBold(True)
            due_item.setFont(due_item_font)
            
            # Status items with status colors
            status_item = QTableWidgetItem(d.status.value)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if d.status.value == "Validated":
                status_item.setForeground(QColor("#34d399"))  # Green
            elif d.status.value == "Submitted":
                status_item.setForeground(QColor("#fbbf24"))  # Orange
            elif d.status.value == "Rejected":
                status_item.setForeground(QColor("#f87171"))  # Red
            else:
                status_item.setForeground(QColor("#94a3b8"))  # Slate Gray (Draft)

            filed_str = d.filed_date.strftime("%Y-%m-%d %H:%M")

            self.table.setItem(idx, 0, ref_item)
            self.table.setItem(idx, 1, QTableWidgetItem(d.taxpayer_name or f"Taxpayer #{d.taxpayer_id}"))
            self.table.setItem(idx, 2, QTableWidgetItem(d.declaration_type))
            self.table.setItem(idx, 3, yr_item)
            self.table.setItem(idx, 4, per_item)
            self.table.setItem(idx, 5, gross_item)
            self.table.setItem(idx, 6, ded_item)
            self.table.setItem(idx, 7, pen_item)
            self.table.setItem(idx, 8, due_item)
            self.table.setItem(idx, 9, status_item)
            self.table.setItem(idx, 10, QTableWidgetItem(filed_str))
            self.table.setItem(idx, 11, QTableWidgetItem(d.rejection_reason or ""))

        self.table.resizeRowsToContents()

    def on_filter_changed(self):
        self.refresh_list()

    def on_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.render_table_page()

    def on_next_page(self):
        total_items = len(self.all_declarations)
        total_pages = (total_items + self.page_size - 1) // self.page_size
        if self.current_page < total_pages:
            self.current_page += 1
            self.render_table_page()

    def get_selected_declaration(self) -> tuple[int, str]:
        """Returns (id, status_string) for the selected row."""
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return None, None
        row = selected_ranges[0].topRow()
        ref_item = self.table.item(row, 0)
        status_item = self.table.item(row, 9)
        if ref_item and status_item:
            return ref_item.data(Qt.ItemDataRole.UserRole), status_item.text()
        return None, None

    def on_selection_changed(self):
        # Update button enable states depending on the status of selected record
        dec_id, status = self.get_selected_declaration()
        role = self.current_user.role

        if not dec_id:
            self.edit_btn.setEnabled(False)
            self.submit_btn.setEnabled(False)
            self.validate_btn.setEnabled(False)
            self.reject_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return

        # Delete is Admin-only, always enabled if row selected and role is Admin
        self.delete_btn.setEnabled(role == UserRole.ADMIN)

        # Edit is allowed if not validated
        self.edit_btn.setEnabled(role in (UserRole.ADMIN, UserRole.EDITOR) and status != "Validated")

        # Submit is allowed if Draft or Rejected
        self.submit_btn.setEnabled(role in (UserRole.ADMIN, UserRole.EDITOR) and status in ("Draft", "Rejected"))

        # Validate/Reject are Admin-only and allowed if status is Submitted or Draft (or Rejected to recheck)
        is_admin = (role == UserRole.ADMIN)
        self.validate_btn.setEnabled(is_admin and status != "Validated")
        self.reject_btn.setEnabled(is_admin and status != "Rejected" and status != "Validated")

    def on_add_clicked(self):
        if self.current_user.role not in (UserRole.ADMIN, UserRole.EDITOR):
            self.message_bar.show_message("Permission Denied: Only Admins or Editors can add declarations.", "error")
            return

        # Verify active taxpayers exist first
        taxpayers = self.taxpayer_service.search_taxpayers()
        if not taxpayers:
            self.message_bar.show_message("No taxpayers exist. Please add a taxpayer before filing a declaration.", "warning")
            return

        dialog = DeclarationDialog(self.declaration_service, self.taxpayer_service, self.current_user, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.message_bar.show_message("Declaration draft created successfully!", "success")
            self.refresh_list()

    def on_edit_clicked(self):
        if self.current_user.role not in (UserRole.ADMIN, UserRole.EDITOR):
            return

        dec_id, status = self.get_selected_declaration()
        if not dec_id:
            self.message_bar.show_message("Please select a declaration to edit.", "warning")
            return

        if status == "Validated":
            self.message_bar.show_message("Validated declarations are locked and cannot be edited.", "warning")
            return

        try:
            declaration = self.declaration_service.get_declaration_by_id(dec_id)
            dialog = DeclarationDialog(self.declaration_service, self.taxpayer_service, self.current_user, declaration, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.message_bar.show_message("Declaration updated successfully!", "success")
                self.refresh_list()
        except Exception as e:
            self.message_bar.show_message(f"Error loading declaration: {str(e)}", "error")

    def on_submit_clicked(self):
        dec_id, _ = self.get_selected_declaration()
        if not dec_id:
            return

        try:
            self.declaration_service.submit_declaration(dec_id, self.current_user)
            self.message_bar.show_message("Declaration submitted for validation successfully.", "success")
            self.refresh_list()
        except Exception as e:
            self.message_bar.show_message(f"Submission failed: {str(e)}", "error")

    def on_validate_clicked(self):
        if self.current_user.role != UserRole.ADMIN:
            return
            
        dec_id, _ = self.get_selected_declaration()
        if not dec_id:
            return

        try:
            self.declaration_service.validate_declaration(dec_id, self.current_user)
            self.message_bar.show_message("Declaration validated and locked successfully.", "success")
            self.refresh_list()
        except Exception as e:
            self.message_bar.show_message(f"Validation failed: {str(e)}", "error")

    def on_reject_clicked(self):
        if self.current_user.role != UserRole.ADMIN:
            return

        dec_id, _ = self.get_selected_declaration()
        if not dec_id:
            return

        dialog = RejectionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                self.declaration_service.reject_declaration(dec_id, dialog.rejection_reason, self.current_user)
                self.message_bar.show_message("Declaration status updated to Rejected.", "success")
                self.refresh_list()
            except Exception as e:
                self.message_bar.show_message(f"Rejection failed: {str(e)}", "error")

    def on_delete_clicked(self):
        if self.current_user.role != UserRole.ADMIN:
            return

        dec_id, _ = self.get_selected_declaration()
        if not dec_id:
            return

        try:
            declaration = self.declaration_service.get_declaration_by_id(dec_id)
            confirm = ConfirmDialog(
                "Delete Declaration",
                f"Are you sure you want to delete declaration '{declaration.reference_number}'?\nThis action cannot be undone.",
                self
            )
            if confirm.exec() == QDialog.DialogCode.Accepted:
                self.declaration_service.delete_declaration(dec_id, self.current_user)
                self.message_bar.show_message("Declaration record deleted successfully.", "success")
                self.refresh_list()
        except Exception as e:
            self.message_bar.show_message(f"Delete failed: {str(e)}", "error")

    def on_export_excel(self):
        if not self.all_declarations:
            self.message_bar.show_message("No data available to export.", "warning")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Declarations to Excel", "declarations_export.xlsx", "Excel Files (*.xlsx)"
        )
        if not file_path:
            return

        try:
            self.declaration_service.export_to_excel(self.all_declarations, file_path)
            self.message_bar.show_message(f"Declarations exported successfully to {file_path}", "success")
        except Exception as e:
            self.message_bar.show_message(f"Excel export failed: {str(e)}", "error")

    def on_export_csv(self):
        if not self.all_declarations:
            self.message_bar.show_message("No data available to export.", "warning")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Declarations to CSV", "declarations_export.csv", "CSV Files (*.csv)"
        )
        if not file_path:
            return

        try:
            self.declaration_service.export_to_csv(self.all_declarations, file_path)
            self.message_bar.show_message(f"Declarations exported successfully to {file_path}", "success")
        except Exception as e:
            self.message_bar.show_message(f"CSV export failed: {str(e)}", "error")
