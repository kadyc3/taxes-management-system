from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QHBoxLayout, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from Kernel.models.declaration import Declaration, DeclarationStatus
from Kernel.exceptions.app_exceptions import ValidationError

class DeclarationDialog(QDialog):
    def __init__(self, declaration_service, taxpayer_service, current_user, declaration: Declaration = None, parent=None):
        super().__init__(parent)
        self.declaration_service = declaration_service
        self.taxpayer_service = taxpayer_service
        self.current_user = current_user
        self.declaration = declaration
        
        self.setWindowTitle("File Declaration" if not declaration else "Edit Declaration")
        self.setModal(True)
        self.setMinimumWidth(450)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Taxpayer select
        self.taxpayer_combo = QComboBox(self)
        self.load_taxpayers()
        form_layout.addRow("Taxpayer *:", self.taxpayer_combo)

        # Reference Number
        self.ref_input = QLineEdit(self)
        self.ref_input.setPlaceholderText("e.g. DEC-2026-001")
        form_layout.addRow("Reference Number *:", self.ref_input)

        # Declaration Type
        self.type_combo = QComboBox(self)
        self.type_combo.addItems(["TVA", "IR", "IS", "Property Tax", "Customs Duty", "Other"])
        self.type_combo.setEditable(True)
        form_layout.addRow("Declaration Type *:", self.type_combo)

        # Fiscal Year
        self.year_input = QSpinBox(self)
        self.year_input.setRange(1900, 2100)
        self.year_input.setValue(2026)
        form_layout.addRow("Fiscal Year *:", self.year_input)

        # Period
        self.period_combo = QComboBox(self)
        self.period_combo.addItems(["Q1", "Q2", "Q3", "Q4", "Monthly", "Annual"])
        self.period_combo.setEditable(True)
        form_layout.addRow("Period *:", self.period_combo)

        # Gross Amount
        self.gross_input = QDoubleSpinBox(self)
        self.gross_input.setRange(0, 999999999.99)
        self.gross_input.setDecimals(2)
        self.gross_input.setPrefix("$ ")
        self.gross_input.valueChanged.connect(self.recalculate_total_due)
        form_layout.addRow("Gross Amount *:", self.gross_input)

        # Deductions
        self.deductions_input = QDoubleSpinBox(self)
        self.deductions_input.setRange(0, 999999999.99)
        self.deductions_input.setDecimals(2)
        self.deductions_input.setPrefix("$ ")
        self.deductions_input.valueChanged.connect(self.recalculate_total_due)
        form_layout.addRow("Deductions *:", self.deductions_input)

        # Penalties
        self.penalties_input = QDoubleSpinBox(self)
        self.penalties_input.setRange(0, 999999999.99)
        self.penalties_input.setDecimals(2)
        self.penalties_input.setPrefix("$ ")
        self.penalties_input.valueChanged.connect(self.recalculate_total_due)
        form_layout.addRow("Penalties *:", self.penalties_input)

        # Total Due (calculated field)
        self.total_due_display = QLabel("$ 0.00", self)
        self.total_due_display.setStyleSheet("font-size: 16px; font-weight: bold; color: #38bdf8;")
        form_layout.addRow("Total Tax Due:", self.total_due_display)

        main_layout.addLayout(form_layout)

        # Validation feedback label
        self.error_label = QLabel("", self)
        self.error_label.setStyleSheet("color: #f87171; font-weight: 500;")
        self.error_label.setWordWrap(True)
        main_layout.addWidget(self.error_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.save_btn = QPushButton("Save Draft", self)
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.clicked.connect(self.on_save_clicked)
        btn_layout.addWidget(self.save_btn)

        main_layout.addLayout(btn_layout)

        if declaration:
            self.load_declaration_data()

    def load_taxpayers(self):
        taxpayers = self.taxpayer_service.search_taxpayers()
        self.taxpayer_combo.clear()
        
        # Populate combobox with UserRole mapping
        for t in taxpayers:
            # We display Name and NIN, store ID in userData
            display_text = f"{t.full_name} ({t.nin})"
            self.taxpayer_combo.addItem(display_text, t.id)

    def load_declaration_data(self):
        d = self.declaration
        # Select correct taxpayer
        index = self.taxpayer_combo.findData(d.taxpayer_id)
        if index >= 0:
            self.taxpayer_combo.setCurrentIndex(index)
            
        self.ref_input.setText(d.reference_number)
        self.type_combo.setCurrentText(d.declaration_type)
        self.year_input.setValue(d.fiscal_year)
        self.period_combo.setCurrentText(d.period)
        self.gross_input.setValue(d.gross_amount)
        self.deductions_input.setValue(d.deductions)
        self.penalties_input.setValue(d.penalties)
        self.recalculate_total_due()

        # Rename button if updating
        self.save_btn.setText("Update Declaration")

    def recalculate_total_due(self):
        gross = self.gross_input.value()
        deductions = self.deductions_input.value()
        penalties = self.penalties_input.value()
        
        total = gross - deductions + penalties
        self.total_due_display.setText(f"$ {total:,.2f}")

    def on_save_clicked(self):
        taxpayer_id = self.taxpayer_combo.currentData()
        if not taxpayer_id:
            self.error_label.setText("You must select a taxpayer.")
            return

        ref_num = self.ref_input.text().strip()
        dec_type = self.type_combo.currentText().strip()
        year = self.year_input.value()
        period = self.period_combo.currentText().strip()
        gross = self.gross_input.value()
        deductions = self.deductions_input.value()
        penalties = self.penalties_input.value()

        try:
            if not self.declaration:
                # Create mode, default status is Draft
                self.declaration = self.declaration_service.create_declaration(
                    taxpayer_id=taxpayer_id,
                    reference_number=ref_num,
                    declaration_type=dec_type,
                    fiscal_year=year,
                    period=period,
                    gross_amount=gross,
                    deductions=deductions,
                    penalties=penalties,
                    current_user=self.current_user,
                    status="Draft"
                )
            else:
                # Edit mode
                self.declaration = self.declaration_service.update_declaration(
                    declaration_id=self.declaration.id,
                    taxpayer_id=taxpayer_id,
                    reference_number=ref_num,
                    declaration_type=dec_type,
                    fiscal_year=year,
                    period=period,
                    gross_amount=gross,
                    deductions=deductions,
                    penalties=penalties,
                    current_user=self.current_user
                )
            self.accept()
        except ValidationError as e:
            self.error_label.setText(str(e))
        except Exception as e:
            self.error_label.setText(f"An unexpected error occurred: {str(e)}")
