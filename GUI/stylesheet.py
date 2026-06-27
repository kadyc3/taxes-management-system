def get_dark_stylesheet() -> str:
    return """
    /* Main Window and Dialogs */
    QMainWindow, QDialog {
        background-color: #0f172a;
        color: #f8fafc;
        font-family: "Segoe UI", -apple-system, sans-serif;
        font-size: 13px;
    }

    /* Sidebar Panel */
    QFrame#SidebarFrame {
        background-color: #1e293b;
        border-right: 1px solid #334155;
        min-width: 220px;
        max-width: 220px;
    }

    /* Main Content Area */
    QFrame#ContentFrame {
        background-color: #0f172a;
    }

    /* Header Panel */
    QFrame#HeaderFrame {
        background-color: #1e293b;
        border-bottom: 1px solid #334155;
        min-height: 60px;
        max-height: 60px;
    }

    /* Cards / Containers */
    QFrame.CardFrame {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
    }

    /* Typography */
    QLabel {
        color: #f8fafc;
    }
    QLabel#HeaderTitle {
        font-size: 18px;
        font-weight: bold;
        color: #f8fafc;
    }
    QLabel#SidebarTitle {
        font-size: 16px;
        font-weight: bold;
        color: #38bdf8;
        margin-bottom: 10px;
    }
    QLabel#KpiValue {
        font-size: 24px;
        font-weight: bold;
        color: #f8fafc;
    }
    QLabel#KpiLabel {
        font-size: 12px;
        color: #94a3b8;
    }

    /* Input Fields (QLineEdit, QComboBox, QSpinBox, QTextEdit) */
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
        background-color: #0f172a;
        border: 1px solid #475569;
        border-radius: 6px;
        padding: 6px 12px;
        color: #f8fafc;
        selection-background-color: #3b82f6;
    }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
        border: 1px solid #3b82f6;
        background-color: #1e293b;
    }
    QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QTextEdit:disabled {
        background-color: #1e293b;
        color: #64748b;
        border: 1px solid #334155;
    }

    /* Buttons (QPushButtons) */
    QPushButton {
        background-color: #334155;
        border: 1px solid #475569;
        border-radius: 6px;
        color: #f8fafc;
        padding: 6px 16px;
        font-weight: 600;
        min-height: 20px;
    }
    QPushButton:hover {
        background-color: #475569;
        border-color: #64748b;
    }
    QPushButton:pressed {
        background-color: #1e293b;
    }

    /* Primary Accent Button */
    QPushButton#PrimaryButton {
        background-color: #3b82f6;
        border: 1px solid #2563eb;
    }
    QPushButton#PrimaryButton:hover {
        background-color: #60a5fa;
        border-color: #3b82f6;
    }
    QPushButton#PrimaryButton:pressed {
        background-color: #1d4ed8;
    }

    /* Success Button */
    QPushButton#SuccessButton {
        background-color: #10b981;
        border: 1px solid #059669;
    }
    QPushButton#SuccessButton:hover {
        background-color: #34d399;
    }
    QPushButton#SuccessButton:pressed {
        background-color: #047857;
    }

    /* Danger Button */
    QPushButton#DangerButton {
        background-color: #ef4444;
        border: 1px solid #dc2626;
    }
    QPushButton#DangerButton:hover {
        background-color: #f87171;
    }
    QPushButton#DangerButton:pressed {
        background-color: #b91c1c;
    }

    /* Warning Button */
    QPushButton#WarningButton {
        background-color: #f59e0b;
        border: 1px solid #d97706;
    }
    QPushButton#WarningButton:hover {
        background-color: #fbbf24;
    }
    QPushButton#WarningButton:pressed {
        background-color: #b45309;
    }

    /* Sidebar Navigation Buttons */
    QPushButton.SidebarBtn {
        background-color: transparent;
        border: none;
        border-radius: 6px;
        color: #94a3b8;
        text-align: left;
        padding: 10px 15px;
        font-size: 14px;
        font-weight: 500;
    }
    QPushButton.SidebarBtn:hover {
        background-color: #334155;
        color: #f8fafc;
    }
    QPushButton.SidebarBtn:checked {
        background-color: #3b82f6;
        color: #ffffff;
        font-weight: bold;
    }

    /* Table Widget Styling */
    QTableWidget {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        gridline-color: #334155;
        color: #f8fafc;
        selection-background-color: #3b82f6;
        selection-color: #ffffff;
    }
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #334155;
    }
    QTableWidget::item:hover {
        background-color: #334155;
    }
    QTableWidget::item:selected {
        background-color: #3b82f6;
    }

    /* Header views for Tables */
    QHeaderView::section {
        background-color: #0f172a;
        color: #94a3b8;
        padding: 6px;
        font-weight: bold;
        border: none;
        border-bottom: 2px solid #334155;
    }

    /* Scrollbars */
    QScrollBar:vertical {
        background-color: #0f172a;
        width: 12px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background-color: #334155;
        min-height: 20px;
        border-radius: 6px;
        margin: 2px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #475569;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QScrollBar:horizontal {
        background-color: #0f172a;
        height: 12px;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background-color: #334155;
        min-width: 20px;
        border-radius: 6px;
        margin: 2px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #475569;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0px;
    }

    /* Tab Widget styling */
    QTabWidget::pane {
        border: 1px solid #334155;
        background-color: #1e293b;
        border-radius: 8px;
    }
    QTabBar::tab {
        background-color: #0f172a;
        color: #94a3b8;
        border: 1px solid #334155;
        border-bottom-color: transparent;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        padding: 8px 16px;
        margin-right: 2px;
    }
    QTabBar::tab:hover {
        background-color: #1e293b;
        color: #f8fafc;
    }
    QTabBar::tab:selected {
        background-color: #1e293b;
        color: #3b82f6;
        border-bottom-color: #1e293b;
        font-weight: bold;
    }

    /* Tooltips */
    QToolTip {
        background-color: #1e293b;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 4px;
        padding: 4px;
    }
    """
