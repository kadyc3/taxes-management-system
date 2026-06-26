# GUI/theme/app_theme.py

APP_STYLESHEET = """
/* ================================
   GLOBAL BASE
================================ */
QWidget {
    font-family: "Segoe UI";
    font-size: 10pt;
    color: #111827;
    background-color: #F9FAFB;
}

/* ================================
   MAIN WINDOW / PANELS
================================ */
QMainWindow {
    background-color: #F9FAFB;
}

/* ================================
   SIDEBAR
================================ */
#Sidebar {
    background-color: #111827;
    color: white;
}

#Sidebar QLabel {
    color: white;
}

#SidebarTitle {
    font-size: 14px;
    font-weight: bold;
    padding: 12px;
}

#SidebarSubtitle {
    font-size: 10px;
    color: #9CA3AF;
    padding: 0 12px 12px 12px;
}

QPushButton#NavButton {
    text-align: left;
    padding: 10px 14px;
    border: none;
    color: #D1D5DB;
    background: transparent;
}

QPushButton#NavButton:hover {
    background-color: #1F2937;
    color: white;
}

QPushButton#NavButton:checked {
    background-color: #2563EB;
    color: white;
    border-left: 3px solid #60A5FA;
}

QPushButton#LogoutButton {
    background-color: #EF4444;
    color: white;
    border-radius: 6px;
    padding: 10px;
}

QPushButton#LogoutButton:hover {
    background-color: #DC2626;
}

/* ================================
   BUTTONS
================================ */
QPushButton {
    background-color: #E5E7EB;
    border-radius: 6px;
    padding: 6px 12px;
}

QPushButton:hover {
    background-color: #D1D5DB;
}

QPushButton#SecondaryButton {
    background-color: #F3F4F6;
}

QPushButton#SecondaryButton:hover {
    background-color: #E5E7EB;
}

QPushButton#DangerButton {
    background-color: #FEE2E2;
    color: #991B1B;
}

QPushButton#DangerButton:hover {
    background-color: #FCA5A5;
}

/* Primary action buttons */
QPushButton#PrimaryButton {
    background-color: #2563EB;
    color: white;
    font-weight: bold;
}

QPushButton#PrimaryButton:hover {
    background-color: #1D4ED8;
}

/* ================================
   TABLES
================================ */
QTableWidget {
    background-color: white;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    gridline-color: #F3F4F6;
}

QHeaderView::section {
    background-color: #F3F4F6;
    padding: 6px;
    border: none;
    font-weight: bold;
}

QTableWidget::item {
    padding: 6px;
}

QTableWidget::item:selected {
    background-color: #DBEAFE;
    color: #111827;
}

/* zebra effect */
QTableWidget {
    alternate-background-color: #F9FAFB;
}

/* ================================
   INPUTS
================================ */
QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 6px;
    background: white;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #2563EB;
}

/* ================================
   LABELS
================================ */
#PageTitle {
    font-size: 18px;
    font-weight: bold;
}

#PageSubtitle {
    font-size: 10px;
    color: #6B7280;
}
"""