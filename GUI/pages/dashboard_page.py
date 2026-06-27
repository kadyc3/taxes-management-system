from __future__ import annotations
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QGridLayout, QFrame, QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer

from GUI.widgets.base_widgets import (
    KpiCard, SectionTitle, PrimaryButton, SecondaryButton, Card, StatusBadge,
)
from GUI.widgets.kpi_card import KpiCard
from GUI.widgets.chart_widgets import BarChartWidget, LineChartWidget, DonutChartWidget
from Kernel.services.dashboard_service import DashboardService, DashboardStats


class DashboardPage(QWidget):
    def __init__(
        self,
        service: DashboardService,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._build_ui()
        self._load_data()

        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("PageScrollArea")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(24, 24, 24, 24)
        self._layout.setSpacing(20)

        self._build_greeting()
        self._build_taxpayer_kpis()
        self._build_declaration_kpis()
        self._build_charts_row()
        self._build_bottom_row()

        self._layout.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)

    def _build_greeting(self) -> None:
        banner = QFrame()
        banner.setObjectName("GreetingBanner")
        row = QHBoxLayout(banner)
        row.setContentsMargins(24, 20, 24, 20)
        row.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(4)
        title = QLabel("Bonjour, Admin")
        title.setObjectName("GreetingTitle")
        sub = QLabel("Here is what is happening across the tax administration today.")
        sub.setObjectName("GreetingSubtitle")
        left.addWidget(title)
        left.addWidget(sub)
        row.addLayout(left)
        row.addStretch()

        clock_box = QFrame()
        clock_box.setObjectName("ClockBox")
        clock_layout = QVBoxLayout(clock_box)
        clock_layout.setContentsMargins(14, 8, 14, 8)
        clock_layout.setSpacing(2)
        self._date_lbl = QLabel()
        self._date_lbl.setObjectName("ClockDate")
        self._date_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._time_lbl = QLabel()
        self._time_lbl.setObjectName("ClockTime")
        self._time_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        clock_layout.addWidget(self._date_lbl)
        clock_layout.addWidget(self._time_lbl)
        row.addWidget(clock_box)

        refresh_btn = PrimaryButton("⟳  Refresh")
        refresh_btn.clicked.connect(self._load_data)
        row.addWidget(refresh_btn)

        self._layout.addWidget(banner)
        self._update_clock()

    def _update_clock(self) -> None:
        from datetime import datetime
        now = datetime.now()
        self._date_lbl.setText(now.strftime("%A, %d %B %Y"))
        self._time_lbl.setText(now.strftime("%H:%M:%S"))

    def _build_taxpayer_kpis(self) -> None:
        self._layout.addWidget(SectionTitle("Taxpayers Overview"))
        self._tp_grid = QGridLayout()
        self._tp_grid.setSpacing(12)
        self._layout.addLayout(self._tp_grid)

    def _build_declaration_kpis(self) -> None:
        self._layout.addWidget(SectionTitle("Declarations Overview"))
        self._dcl_grid = QGridLayout()
        self._dcl_grid.setSpacing(12)
        self._layout.addLayout(self._dcl_grid)

    def _build_charts_row(self) -> None:
        self._layout.addWidget(SectionTitle("Analytics"))
        charts_row = QHBoxLayout()
        charts_row.setSpacing(16)

        bar_card = QFrame()
        bar_card.setObjectName("ChartWidget")
        bar_layout = QVBoxLayout(bar_card)
        bar_layout.setContentsMargins(0, 0, 0, 8)
        self._bar_chart = BarChartWidget(
            "Declarations per Month",
            [],
            ("Total", "Validated"),
            ("#2563eb", "#16a34a"),
        )
        bar_layout.addWidget(self._bar_chart)
        charts_row.addWidget(bar_card, 3)

        donut_card = QFrame()
        donut_card.setObjectName("ChartWidget")
        donut_layout = QVBoxLayout(donut_card)
        donut_layout.setContentsMargins(0, 0, 0, 8)
        self._donut_chart = DonutChartWidget("Declaration Status", [])
        donut_layout.addWidget(self._donut_chart)
        charts_row.addWidget(donut_card, 2)

        self._layout.addLayout(charts_row)

    def _build_bottom_row(self) -> None:
        row = QHBoxLayout()
        row.setSpacing(16)

        # Recent activity
        activity_card = QFrame()
        activity_card.setObjectName("Card")
        act_layout = QVBoxLayout(activity_card)
        act_layout.setContentsMargins(20, 16, 20, 16)
        act_layout.setSpacing(10)
        act_title = SectionTitle("Recent Activity")
        act_layout.addWidget(act_title)
        self._activity_layout = QVBoxLayout()
        self._activity_layout.setSpacing(6)
        act_layout.addLayout(self._activity_layout)
        row.addWidget(activity_card, 3)

        # Alerts
        alerts_card = QFrame()
        alerts_card.setObjectName("Card")
        alert_layout = QVBoxLayout(alerts_card)
        alert_layout.setContentsMargins(20, 16, 20, 16)
        alert_layout.setSpacing(10)
        alert_title = SectionTitle("Alerts")
        alert_layout.addWidget(alert_title)
        self._alerts_layout = QVBoxLayout()
        self._alerts_layout.setSpacing(8)
        alert_layout.addLayout(self._alerts_layout)
        alert_layout.addStretch()
        row.addWidget(alerts_card, 2)

        self._layout.addLayout(row)

    def _load_data(self) -> None:
        stats = self._service.get_stats()
        self._populate_tp_kpis(stats)
        self._populate_dcl_kpis(stats)
        self._populate_charts(stats)
        self._populate_activity(stats)
        self._populate_alerts(stats)

    def _clear_layout(self, layout: QGridLayout | QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _populate_tp_kpis(self, stats: DashboardStats) -> None:
        self._clear_layout(self._tp_grid)
        cards = [
            ("Total Taxpayers", str(stats.total_taxpayers), "♟", "blue",
             ("4.2%", True)),
            ("Active", str(stats.active_taxpayers), "✓", "green",
             ("2.1%", True)),
            ("Suspended", str(stats.suspended_taxpayers), "⏸", "orange",
             ("0.8%", False)),
            ("Deregistered", str(stats.deregistered_taxpayers), "✕", "red",
             ("1.3%", False)),
        ]
        for col, (lbl, val, icon, accent, trend) in enumerate(cards):
            card = KpiCard(lbl, val, icon, accent=accent, trend=trend)
            self._tp_grid.addWidget(card, 0, col)

    def _populate_dcl_kpis(self, stats: DashboardStats) -> None:
        self._clear_layout(self._dcl_grid)
        amount_str = f"{stats.total_taxes_due:,.0f} TND"
        cards = [
            ("Total Declarations", str(stats.total_declarations), "◫", "blue", None),
            ("Draft", str(stats.draft_declarations), "◻", "orange", None),
            ("Submitted", str(stats.submitted_declarations), "◈", "darkblue", None),
            ("Validated", str(stats.validated_declarations), "◉", "green", None),
            ("Rejected", str(stats.rejected_declarations), "◐", "red", None),
            ("Total Taxes Due", amount_str, "₺", "blue", None),
        ]
        for col, (lbl, val, icon, accent, trend) in enumerate(cards):
            card = KpiCard(lbl, val, icon, accent=accent)
            self._dcl_grid.addWidget(card, 0, col)

    def _populate_charts(self, stats: DashboardStats) -> None:
        monthly = stats.monthly_stats
        bar_data = []
        for row in monthly:
            month_label = row.get("month", "")[-2:] or row.get("month", "")
            bar_data.append((
                month_label,
                float(row.get("total", 0)),
                float(row.get("validated", 0)),
            ))
        self._bar_chart.update_data(bar_data)

        donut_data = [
            ("Validated", stats.validated_declarations, "#16a34a"),
            ("Submitted", stats.submitted_declarations, "#2563eb"),
            ("Draft", stats.draft_declarations, "#f59e0b"),
            ("Rejected", stats.rejected_declarations, "#dc2626"),
        ]
        self._donut_chart.update_data([d for d in donut_data if d[1] > 0])

    def _populate_activity(self, stats: DashboardStats) -> None:
        while self._activity_layout.count():
            item = self._activity_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        severity_icons = {
            "success": ("✓", "#dcfce7", "#16a34a"),
            "info": ("ℹ", "#dbeafe", "#2563eb"),
            "warning": ("⚠", "#fef3c7", "#92400e"),
            "danger": ("✕", "#fee2e2", "#dc2626"),
        }

        for log in stats.recent_logs[:5]:
            item = QFrame()
            item.setObjectName("ActivityItem")
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(10, 8, 10, 8)
            item_layout.setSpacing(10)

            sev = log.severity.value
            ch, bg, fg = severity_icons.get(sev, ("ℹ", "#dbeafe", "#2563eb"))
            icon_lbl = QLabel(ch)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setFixedSize(28, 28)
            icon_lbl.setStyleSheet(
                f"background-color: {bg}; color: {fg}; "
                f"border-radius: 8px; font-weight: 700;"
            )
            item_layout.addWidget(icon_lbl)

            text_col = QVBoxLayout()
            text_col.setSpacing(1)
            title = QLabel(log.description[:60])
            title.setObjectName("ActivityTitle")
            meta = QLabel(f"{log.action}  ·  {log.date}")
            meta.setObjectName("ActivityMeta")
            text_col.addWidget(title)
            text_col.addWidget(meta)
            item_layout.addLayout(text_col)

            self._activity_layout.addWidget(item)

    def _populate_alerts(self, stats: DashboardStats) -> None:
        while self._alerts_layout.count():
            item = self._alerts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        alerts = [
            ("Draft declarations waiting", stats.draft_declarations, "warning"),
            ("Rejected declarations", stats.rejected_declarations, "danger"),
            ("Suspended taxpayers", stats.suspended_taxpayers, "warning"),
        ]
        for label, value, kind in alerts:
            frame = QFrame()
            frame.setObjectName("AlertWarning" if kind == "warning" else "AlertDanger")
            row = QHBoxLayout(frame)
            row.setContentsMargins(12, 10, 12, 10)
            lbl = QLabel(label)
            lbl.setObjectName("AlertWarningLabel" if kind == "warning" else "AlertDangerLabel")
            val_lbl = QLabel(str(value))
            val_lbl.setStyleSheet("font-weight: 700; font-size: 14px;")
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val_lbl)
            self._alerts_layout.addWidget(frame)