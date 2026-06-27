from __future__ import annotations
from typing import Optional
from PyQt6.QtWidgets import QWidget, QLabel
from GUI.dialogs.base_dialog import BaseDialog
from GUI.widgets.base_widgets import DangerButton, SecondaryButton


class ConfirmDeleteDialog(BaseDialog):
    def __init__(
        self,
        entity_name: str,
        entity_type: str = "record",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(
            title=f"Delete {entity_type}",
            subtitle="This action cannot be undone.",
            parent=parent,
            min_width=420,
        )
        msg = QLabel(
            f'Are you sure you want to delete <b>"{entity_name}"</b>?<br>'
            f"This will permanently remove the {entity_type.lower()} from the system."
        )
        msg.setWordWrap(True)
        msg.setStyleSheet("font-size: 13px; color: #374151; line-height: 1.5;")
        self.add_content_widget(msg)

        cancel_btn = SecondaryButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        delete_btn = DangerButton(f"Delete {entity_type}")
        delete_btn.clicked.connect(self.accept)
        self.add_button_row(cancel_btn, delete_btn)


class RejectDeclarationDialog(BaseDialog):
    def __init__(self, number: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(
            title="Reject Declaration",
            subtitle=f"Provide a reason for rejecting {number}.",
            parent=parent,
            min_width=440,
        )
        from PyQt6.QtWidgets import QLineEdit
        from GUI.widgets.base_widgets import FieldLabel
        self.add_content_widget(FieldLabel("Rejection Reason *"))
        self._reason = QLineEdit()
        self._reason.setPlaceholderText("e.g. Missing supporting invoice")
        self.add_content_widget(self._reason)

        self._error_lbl = QLabel("")
        self._error_lbl.setStyleSheet("color: #dc2626; font-size: 12px;")
        self._error_lbl.hide()
        self.add_content_widget(self._error_lbl)

        cancel_btn = SecondaryButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        reject_btn = DangerButton("Reject Declaration")
        reject_btn.clicked.connect(self._on_reject)
        self.add_button_row(cancel_btn, reject_btn)

    def _on_reject(self) -> None:
        if not self._reason.text().strip():
            self._error_lbl.setText("Reason is required.")
            self._error_lbl.show()
            return
        self.accept()

    def get_reason(self) -> str:
        return self._reason.text().strip()