from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QTextEdit, QHBoxLayout, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from Kernel.models.taxpayer import Taxpayer, TaxpayerType, TaxpayerStatus
from Kernel.exceptions.app_exceptions import ValidationError

class TaxpayerDialog(QDialog):
    def __init__(self, taxpayer_service, current_user, taxpayer: Taxpayer = None, parent=None):
        super().__init__(parent)
        self.taxpayer_service = taxpayer_service
        self.current_user = current_user
        self.taxpayer = taxpayer
        
        self.setWindowTitle("Add Taxpayer" if not taxpayer else "Edit Taxpayer")
        self.setModal(True)
        self.setMinimumWidth(400)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.full_name_input = QLineEdit(self)
        self.full_name_input.setPlaceholderText("Enter full name")
        form_layout.addRow("Full Name *:", self.full_name_input)

        self.nin_input = QLineEdit(self)
        self.nin_input.setPlaceholderText("Enter national identification number")
        form_layout.addRow("NIN *:", self.nin_input)

        self.type_combo = QComboBox(self)
        self.type_combo.addItems([t.value for t in TaxpayerType])
        form_layout.addRow("Type:", self.type_combo)

        self.status_combo = QComboBox(self)
        self.status_combo.addItems([s.value for s in TaxpayerStatus])
        form_layout.addRow("Status:", self.status_combo)

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText("example@domain.com")
        form_layout.addRow("Email:", self.email_input)

        self.phone_input = QLineEdit(self)
        self.phone_input.setPlaceholderText("+123 456789")
        form_layout.addRow("Phone:", self.phone_input)

        self.address_input = QTextEdit(self)
        self.address_input.setPlaceholderText("Enter street, city, country")
        self.address_input.setMaximumHeight(80)
        form_layout.addRow("Address:", self.address_input)

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

        self.save_btn = QPushButton("Save", self)
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.clicked.connect(self.on_save_clicked)
        btn_layout.addWidget(self.save_btn)

        main_layout.addLayout(btn_layout)

        if taxpayer:
            self.load_taxpayer_data()

    def load_taxpayer_data(self):
        t = self.taxpayer
        self.full_name_input.setText(t.full_name)
        self.nin_input.setText(t.nin)
        self.type_combo.setCurrentText(t.taxpayer_type.value)
        self.status_combo.setCurrentText(t.status.value)
        self.email_input.setText(t.email)
        self.phone_input.setText(t.phone)
        self.address_input.setPlainText(t.address)

    def on_save_clicked(self):
        full_name = self.full_name_input.text().strip()
        nin = self.nin_input.text().strip()
        t_type = self.type_combo.currentText()
        status = self.status_combo.currentText()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        address = self.address_input.toPlainText().strip()

        try:
            if not self.taxpayer:
                # Create mode
                self.taxpayer = self.taxpayer_service.create_taxpayer(
                    nin=nin,
                    full_name=full_name,
                    taxpayer_type=t_type,
                    status=status,
                    email=email,
                    phone=phone,
                    address=address,
                    current_user=self.current_user
                )
            else:
                # Edit mode
                self.taxpayer = self.taxpayer_service.update_taxpayer(
                    taxpayer_id=self.taxpayer.id,
                    nin=nin,
                    full_name=full_name,
                    taxpayer_type=t_type,
                    status=status,
                    email=email,
                    phone=phone,
                    address=address,
                    current_user=self.current_user
                )
            self.accept()
        except ValidationError as e:
            self.error_label.setText(str(e))
        except Exception as e:
            self.error_label.setText(f"An unexpected error occurred: {str(e)}")
