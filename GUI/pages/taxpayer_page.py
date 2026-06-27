from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QHeaderView, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from ..widgets.search_bar import SearchBar
from ..widgets.message_bar import MessageBar
from ..dialogs.taxpayer_dialog import TaxpayerDialog
from ..dialogs.confirm_dialog import ConfirmDialog
from Kernel.models.user import UserRole
from Kernel.exceptions.app_exceptions import PermissionDeniedError

class TaxpayerPage(QWidget):
    def __init__(self, taxpayer_service, current_user, parent=None):
        super().__init__(parent)
        self.taxpayer_service = taxpayer_service
        self.current_user = current_user
        
        # Pagination state
        self.all_taxpayers = []
        self.current_page = 1
        self.page_size = 10

        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title and notification area
        header_hbox = QHBoxLayout()
        title = QLabel("Taxpayers Registry", self)
        title.setObjectName("HeaderTitle")
        header_hbox.addWidget(title)
        
        self.message_bar = MessageBar(self)
        header_hbox.addWidget(self.message_bar, 1)
        layout.addLayout(header_hbox)

        # Toolbar Frame (filters, search, CRUD buttons)
        toolbar_frame = QFrame(self)
        toolbar_frame.setObjectName("CardFrame")
        toolbar_frame.setProperty("class", "CardFrame")
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(15, 10, 15, 10)
        toolbar_layout.setSpacing(10)

        # Search Bar
        self.search_bar = SearchBar("Search by NIN, name, email...", toolbar_frame)
        self.search_bar.textChanged.connect(self.on_filter_changed)
        toolbar_layout.addWidget(self.search_bar, 2)

        # Filters
        self.type_filter = QComboBox(toolbar_frame)
        self.type_filter.addItems(["All Types", "Individual", "Company"])
        self.type_filter.currentIndexChanged.connect(self.on_filter_changed)
        toolbar_layout.addWidget(self.type_filter, 1)

        self.status_filter = QComboBox(toolbar_frame)
        self.status_filter.addItems(["All Statuses", "Active", "Suspended", "Deregistered"])
        self.status_filter.currentIndexChanged.connect(self.on_filter_changed)
        toolbar_layout.addWidget(self.status_filter, 1)

        # Spacer
        toolbar_layout.addStretch(1)

        # Action Buttons
        self.add_btn = QPushButton("Add Taxpayer", toolbar_frame)
        self.add_btn.setObjectName("PrimaryButton")
        self.add_btn.clicked.connect(self.on_add_clicked)
        toolbar_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("Edit", toolbar_frame)
        self.edit_btn.clicked.connect(self.on_edit_clicked)
        toolbar_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton("Delete", toolbar_frame)
        self.delete_btn.setObjectName("DangerButton")
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        toolbar_layout.addWidget(self.delete_btn)

        layout.addWidget(toolbar_frame)

        # Table Grid
        self.table = QTableWidget(self)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "NIN", "Full Name", "Type", "Status", "Email", "Phone", "Address", "Registered"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Name stretches
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_edit_clicked)
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

        # Configure Role-based UI features
        self.apply_role_permissions()
        
        # Load Initial Data
        self.refresh_list()

    def apply_role_permissions(self):
        role = self.current_user.role
        if role == UserRole.ADMIN:
            # Full permissions
            self.add_btn.setVisible(True)
            self.edit_btn.setVisible(True)
            self.delete_btn.setVisible(True)
        elif role == UserRole.EDITOR:
            # Editor cannot delete
            self.add_btn.setVisible(True)
            self.edit_btn.setVisible(True)
            self.delete_btn.setVisible(False)
        else:
            # User is read-only
            self.add_btn.setVisible(False)
            self.edit_btn.setVisible(False)
            self.delete_btn.setVisible(False)

    def refresh_list(self):
        # Fetch status filter value
        status_text = self.status_filter.currentText()
        status_val = None if status_text == "All Statuses" else status_text

        # Fetch type filter value
        type_text = self.type_filter.currentText()
        type_val = None if type_text == "All Types" else type_text

        query = self.search_bar.text().strip()

        # Call service to find taxpayers
        try:
            self.all_taxpayers = self.taxpayer_service.search_taxpayers(query, status_val, type_val)
            
            # Setup Autocomplete suggestions list (Names & NINs)
            autocomplete_terms = []
            for t in self.all_taxpayers:
                if t.full_name not in autocomplete_terms:
                    autocomplete_terms.append(t.full_name)
                if t.nin not in autocomplete_terms:
                    autocomplete_terms.append(t.nin)
            self.search_bar.set_autocomplete_list(autocomplete_terms)

            # Reset page
            self.current_page = 1
            self.render_table_page()
        except Exception as e:
            self.message_bar.show_message(f"Error fetching taxpayers: {str(e)}", "error")

    def render_table_page(self):
        # Calculate pagination limits
        total_items = len(self.all_taxpayers)
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
        page_items = self.all_taxpayers[start_idx:end_idx]

        self.table.setRowCount(0)
        
        for idx, t in enumerate(page_items):
            self.table.insertRow(idx)
            
            # Save ID in item custom role on the first column for reference
            nin_item = QTableWidgetItem(t.nin)
            nin_item.setData(Qt.ItemDataRole.UserRole, t.id)
            nin_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            type_item = QTableWidgetItem(t.taxpayer_type.value)
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            status_item = QTableWidgetItem(t.status.value)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Badge colors for statuses
            if t.status.value == "Active":
                status_item.setForeground(QColor("#34d399"))  # Green
            elif t.status.value == "Suspended":
                status_item.setForeground(QColor("#fbbf24"))  # Orange
            else:
                status_item.setForeground(QColor("#f87171"))  # Red

            reg_str = t.registration_date.strftime("%Y-%m-%d")

            self.table.setItem(idx, 0, nin_item)
            self.table.setItem(idx, 1, QTableWidgetItem(t.full_name))
            self.table.setItem(idx, 2, type_item)
            self.table.setItem(idx, 3, status_item)
            self.table.setItem(idx, 4, QTableWidgetItem(t.email))
            self.table.setItem(idx, 5, QTableWidgetItem(t.phone))
            self.table.setItem(idx, 6, QTableWidgetItem(t.address))
            
            reg_item = QTableWidgetItem(reg_str)
            reg_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(idx, 7, reg_item)

        self.table.resizeRowsToContents()

    def on_filter_changed(self):
        self.refresh_list()

    def on_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.render_table_page()

    def on_next_page(self):
        total_items = len(self.all_taxpayers)
        total_pages = (total_items + self.page_size - 1) // self.page_size
        if self.current_page < total_pages:
            self.current_page += 1
            self.render_table_page()

    def get_selected_taxpayer_id(self) -> int:
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return None
        row = selected_ranges[0].topRow()
        nin_item = self.table.item(row, 0)
        if nin_item:
            return nin_item.data(Qt.ItemDataRole.UserRole)
        return None

    def on_add_clicked(self):
        if self.current_user.role not in (UserRole.ADMIN, UserRole.EDITOR):
            self.message_bar.show_message("Permission Denied: Only Admins or Editors can add taxpayers.", "error")
            return

        dialog = TaxpayerDialog(self.taxpayer_service, self.current_user, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.message_bar.show_message("Taxpayer created successfully!", "success")
            self.refresh_list()

    def on_edit_clicked(self):
        if self.current_user.role not in (UserRole.ADMIN, UserRole.EDITOR):
            return  # Read-only user double clicks don't edit

        taxpayer_id = self.get_selected_taxpayer_id()
        if not taxpayer_id:
            self.message_bar.show_message("Please select a taxpayer to edit.", "warning")
            return

        try:
            taxpayer = self.taxpayer_service.get_taxpayer_by_id(taxpayer_id)
            dialog = TaxpayerDialog(self.taxpayer_service, self.current_user, taxpayer, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.message_bar.show_message("Taxpayer updated successfully!", "success")
                self.refresh_list()
        except Exception as e:
            self.message_bar.show_message(f"Error loading taxpayer: {str(e)}", "error")

    def on_delete_clicked(self):
        if self.current_user.role != UserRole.ADMIN:
            self.message_bar.show_message("Permission Denied: Only Administrators can delete records.", "error")
            return

        taxpayer_id = self.get_selected_taxpayer_id()
        if not taxpayer_id:
            self.message_bar.show_message("Please select a taxpayer to delete.", "warning")
            return

        try:
            taxpayer = self.taxpayer_service.get_taxpayer_by_id(taxpayer_id)
            
            confirm = ConfirmDialog(
                "Delete Taxpayer",
                f"Are you sure you want to delete taxpayer '{taxpayer.full_name}' (NIN: {taxpayer.nin})?\n\nWARNING: All associated declarations will also be deleted.",
                self
            )
            
            if confirm.exec() == QDialog.DialogCode.Accepted:
                self.taxpayer_service.delete_taxpayer(taxpayer_id, self.current_user)
                self.message_bar.show_message("Taxpayer and all declarations deleted successfully.", "success")
                self.refresh_list()
        except Exception as e:
            self.message_bar.show_message(f"Delete failed: {str(e)}", "error")
            self.refresh_list()
