# GUI/widgets/stat_card.py
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt


class StatCard(QFrame):
    """
    Simple dashboard stat card (used in DashboardWindow).
    """

    def __init__(self, title: str, value: str = "—", subtitle: str = "", color: str = "#2563EB"):
        super().__init__()

        self._title = title
        self._value = value
        self._subtitle = subtitle
        self._color = color

        self.setObjectName("StatCard")
        self.setStyleSheet(self._base_style())

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet("font-size: 11px; color: #6B7280;")

        self.value_label = QLabel(self._value)
        self.value_label.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {self._color};"
        )

        self.subtitle_label = QLabel(self._subtitle)
        self.subtitle_label.setStyleSheet("font-size: 10px; color: #9CA3AF;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.subtitle_label)

    def set_value(self, value: str):
        self.value_label.setText(value)

    def _base_style(self) -> str:
        return """
        QFrame#StatCard {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
        }
        """