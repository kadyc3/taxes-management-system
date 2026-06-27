from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt
from ..widgets.charts import DonutChartWidget, BarChartWidget

class DashboardPage(QWidget):
    def __init__(self, dashboard_service, parent=None):
        super().__init__(parent)
        self.dashboard_service = dashboard_service
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header Title
        title = QLabel("Dashboard Summary", self)
        title.setObjectName("HeaderTitle")
        layout.addWidget(title)

        # 1. KPI Cards Grid
        kpi_layout = QGridLayout()
        kpi_layout.setSpacing(15)

        self.revenue_card = self.create_kpi_card("Total Revenue (Validated)", "$ 0.00", "#38bdf8")
        self.taxpayers_card = self.create_kpi_card("Total Taxpayers", "0", "#10b981")
        self.declarations_card = self.create_kpi_card("Total Declarations", "0", "#6366f1")
        self.pending_card = self.create_kpi_card("Pending Validation", "0", "#f59e0b")

        kpi_layout.addWidget(self.revenue_card, 0, 0)
        kpi_layout.addWidget(self.taxpayers_card, 0, 1)
        kpi_layout.addWidget(self.declarations_card, 0, 2)
        kpi_layout.addWidget(self.pending_card, 0, 3)

        layout.addLayout(kpi_layout)

        # 2. Charts Section (Horizontal Layout)
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)

        # Revenue Chart Card
        rev_frame = QFrame(self)
        rev_frame.setObjectName("CardFrame")
        rev_frame.setProperty("class", "CardFrame")
        rev_vbox = QVBoxLayout(rev_frame)
        rev_title = QLabel("Revenue History (Validated)", rev_frame)
        rev_title.setStyleSheet("font-weight: 600; color: #94a3b8;")
        rev_vbox.addWidget(rev_title)
        self.revenue_chart = BarChartWidget(rev_frame)
        rev_vbox.addWidget(self.revenue_chart)
        charts_layout.addWidget(rev_frame, 3)

        # Declaration Statuses Chart Card
        status_frame = QFrame(self)
        status_frame.setObjectName("CardFrame")
        status_frame.setProperty("class", "CardFrame")
        status_vbox = QVBoxLayout(status_frame)
        status_title = QLabel("Declarations Spread", status_frame)
        status_title.setStyleSheet("font-weight: 600; color: #94a3b8;")
        status_vbox.addWidget(status_title)
        
        # Donut wrapper to put chart and legend side by side
        donut_hbox = QHBoxLayout()
        self.donut_chart = DonutChartWidget(status_frame)
        donut_hbox.addWidget(self.donut_chart, 2)
        
        # Legend layout
        self.legend_label = QLabel(status_frame)
        self.legend_label.setStyleSheet("color: #94a3b8; font-size: 11px;")
        donut_hbox.addWidget(self.legend_label, 1)
        
        status_vbox.addLayout(donut_hbox)
        charts_layout.addWidget(status_frame, 2)

        layout.addLayout(charts_layout)

        # 3. Recent Audit Logs / Activities Feed
        feed_frame = QFrame(self)
        feed_frame.setObjectName("CardFrame")
        feed_frame.setProperty("class", "CardFrame")
        feed_vbox = QVBoxLayout(feed_frame)
        
        feed_title = QLabel("Recent System Activities", feed_frame)
        feed_title.setStyleSheet("font-weight: 600; color: #94a3b8;")
        feed_vbox.addWidget(feed_title)

        self.activity_table = QTableWidget(feed_frame)
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Timestamp", "User", "Action", "Details"])
        self.activity_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.activity_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.activity_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.activity_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.activity_table.setMinimumHeight(150)
        self.activity_table.setStyleSheet("border: none; background: transparent;")
        
        feed_vbox.addWidget(self.activity_table)
        layout.addWidget(feed_frame)

        self.refresh_data()

    def create_kpi_card(self, label: str, default_val: str, accent_color: str) -> QFrame:
        card = QFrame(self)
        card.setObjectName("CardFrame")
        card.setProperty("class", "CardFrame")
        card.setStyleSheet(f"border-left: 4px solid {accent_color};")
        
        vbox = QVBoxLayout(card)
        vbox.setContentsMargins(15, 12, 15, 12)
        vbox.setSpacing(5)

        lbl = QLabel(label, card)
        lbl.setObjectName("KpiLabel")
        vbox.addWidget(lbl)

        val = QLabel(default_val, card)
        val.setObjectName("KpiValue")
        vbox.addWidget(val)

        return card

    def update_kpi_card_value(self, card: QFrame, new_value: str):
        val_label = card.findChild(QLabel, "KpiValue")
        if val_label:
            val_label.setText(new_value)

    def refresh_data(self):
        # Fetch KPIs
        kpis = self.dashboard_service.get_kpis()

        # Update KPI Cards
        self.update_kpi_card_value(self.revenue_card, f"$ {kpis['total_revenue']:,.2f}")
        self.update_kpi_card_value(self.taxpayers_card, f"{kpis['taxpayers']['total']}")
        self.update_kpi_card_value(self.declarations_card, f"{kpis['declarations']['total']}")
        self.update_kpi_card_value(self.pending_card, f"{kpis['declarations']['submitted']}")

        # Update Bar Chart (Revenue by year)
        revenue_data = self.dashboard_service.get_revenue_by_year()
        chart_bars = [(str(row["fiscal_year"]), row["revenue"]) for row in revenue_data]
        self.revenue_chart.set_data(chart_bars)

        # Update Donut Chart (Declaration spread)
        dec_kpis = kpis["declarations"]
        donut_data = {
            "Draft": dec_kpis.get("draft", 0),
            "Submitted": dec_kpis.get("submitted", 0),
            "Validated": dec_kpis.get("validated", 0),
            "Rejected": dec_kpis.get("rejected", 0)
        }
        
        colors = {
            "Draft": QColor("#94a3b8"),       # Slate Gray
            "Submitted": QColor("#f59e0b"),   # Amber Orange
            "Validated": QColor("#10b981"),   # Emerald Green
            "Rejected": QColor("#ef4444")     # Crimson Rose
        }
        self.donut_chart.set_data(donut_data, colors)

        # Update Legend Label
        legend_text = f"""
        <span style="color: #94a3b8;">■</span> Draft: {donut_data['Draft']}<br>
        <span style="color: #f59e0b;">■</span> Submitted: {donut_data['Submitted']}<br>
        <span style="color: #10b981;">■</span> Validated: {donut_data['Validated']}<br>
        <span style="color: #ef4444;">■</span> Rejected: {donut_data['Rejected']}
        """
        self.legend_label.setText(legend_text)

        # Update Activities Feed Table
        logs = self.dashboard_service.get_recent_activity(10)
        self.activity_table.setRowCount(0)
        
        for idx, log in enumerate(logs):
            self.activity_table.insertRow(idx)
            
            # Format timestamp nicely
            ts_str = log.created_at.strftime("%Y-%m-%d %H:%M:%S")
            
            self.activity_table.setItem(idx, 0, QTableWidgetItem(ts_str))
            self.activity_table.setItem(idx, 1, QTableWidgetItem(log.username))
            
            action_item = QTableWidgetItem(log.action.upper())
            # Color actions for nice visual cues
            if "create" in log.action or "seed" in log.action:
                action_item.setForeground(QColor("#34d399"))
            elif "delete" in log.action or "failed" in log.action:
                action_item.setForeground(QColor("#f87171"))
            elif "validate" in log.action:
                action_item.setForeground(QColor("#60a5fa"))
            elif "reject" in log.action:
                action_item.setForeground(QColor("#fbbf24"))
                
            self.activity_table.setItem(idx, 2, action_item)
            self.activity_table.setItem(idx, 3, QTableWidgetItem(log.details or ""))

        self.activity_table.resizeRowsToContents()
