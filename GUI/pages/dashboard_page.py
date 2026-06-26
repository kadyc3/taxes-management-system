from PyQt6.QtWidgets import (
    QHeaderView, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QTableWidget, QTableWidgetItem,
    QSizePolicy
)
from PyQt6.QtCore import Qt


def _card(title, value):
    card = QFrame()
    card.setStyleSheet("""
        QFrame {
            background: white;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
        }
        QLabel {
            border: none;
        }
        QLabel#title {
            color: #6B7280;
            font-size: 12px;
        }
        QLabel#value {
            font-size: 20px;
            font-weight: bold;
            color: #111827;
        }
    """)

    layout = QVBoxLayout(card)
    layout.setContentsMargins(14, 12, 14, 12)

    t = QLabel(title)
    t.setObjectName("title")

    v = QLabel(str(value))
    v.setObjectName("value")

    layout.addWidget(t)
    layout.addWidget(v)

    return card


class DashboardPage(QWidget):

    def __init__(self, dashboard_service):
        super().__init__()
        self.service = dashboard_service

        self._build_ui()
        self.refresh()

    # ---------------- UI ----------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # TITLE
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        # KPI ROW
        self.kpi_row = QHBoxLayout()
        layout.addLayout(self.kpi_row)

        # RECENT TABLE
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Date", "Action", "Entity", "User"])
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(300)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.table)

        # ALERTS
        self.alerts = QLabel("")
        self.alerts.setStyleSheet("""
            background: #FEF2F2;
            color: #B91C1C;
            padding: 10px;
            border-radius: 8px;
        """)
        layout.addWidget(self.alerts)

    # ---------------- DATA ----------------
    def refresh(self):
        stats = self.service.get_stats() or {}

        # IMPORTANT: define recent FIRST
        recent = self.service.get_recent() or []

        print("STATUSES:", stats)
        print("RECENT:", recent)

        # fallback safety
        total = stats.get("total", 0)
        draft = stats.get("draft", 0)
        validated = stats.get("validated", 0)
        rejected = stats.get("rejected", 0)
        taxpayers = stats.get("taxpayers", 0)

        # KPI update
        while self.kpi_row.count():
            item = self.kpi_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.kpi_row.addWidget(_card("Taxpayers", taxpayers))
        self.kpi_row.addWidget(_card("Total", total))
        self.kpi_row.addWidget(_card("Draft", draft))
        self.kpi_row.addWidget(_card("Validated", validated))

        # table
        self.table.setRowCount(len(recent))

        for i, r in enumerate(recent):
            self.table.setItem(i, 0, QTableWidgetItem(str(r.get("date", ""))))
            self.table.setItem(i, 1, QTableWidgetItem(str(r.get("action", ""))))
            self.table.setItem(i, 2, QTableWidgetItem(str(r.get("entity", ""))))
            self.table.setItem(i, 3, QTableWidgetItem(str(r.get("user", ""))))

        # alerts
        alerts = []
        if draft > 0:
            alerts.append(f"{draft} drafts pending")
        if rejected > 0:
            alerts.append(f"{rejected} rejected")

        self.alerts.setText("\n".join(alerts) if alerts else "No alerts 🎉")