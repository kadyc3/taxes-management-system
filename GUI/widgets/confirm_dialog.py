"""
GUI/widgets/confirm_dialog.py

A simple modal confirmation dialog used before destructive actions.
"""

from __future__ import annotations
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt


def confirm(
    parent,
    title: str = "Confirm",
    message: str = "Are you sure you want to proceed?",
) -> bool:
    """
    Show a Yes/No modal dialog.

    Returns
    -------
    bool  True if the user clicked Yes.
    """
    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(message)
    dialog.setIcon(QMessageBox.Icon.Warning)
    dialog.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    dialog.setDefaultButton(QMessageBox.StandardButton.No)
    dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
    result = dialog.exec()
    return result == QMessageBox.StandardButton.Yes