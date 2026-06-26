from PyQt6.QtWidgets import QWidget, QVBoxLayout

class Card(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("Card")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(12)