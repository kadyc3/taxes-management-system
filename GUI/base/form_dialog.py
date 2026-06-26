from PyQt6.QtWidgets import QDialog, QVBoxLayout

class BaseFormDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(True)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)