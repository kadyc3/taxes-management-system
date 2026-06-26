from PyQt6.QtWidgets import QWidget, QHBoxLayout

class ActionRow(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout(self)
        self.layout.addStretch()
        self.layout.setSpacing(8)

    def add_button(self, btn):
        self.layout.addWidget(btn)