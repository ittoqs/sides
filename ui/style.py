from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor

# Modern premium color palette
# Primary: #1a365d (Navy)
# Primary Hover: #2a4d7c
# Background: #f8fafc (Slate Off-White)
# Sidebar: #0f172a (Slate Dark Blue)
# Text Main: #1e293b (Slate Gray)
# Accent Success: #10b981 (Emerald)
# Accent Warning: #f59e0b (Amber)
# Accent Danger: #ef4444 (Rose Red)
# Card Background: #ffffff

STYLE_SHEET = """
QMainWindow {
    background-color: #f8fafc;
}

/* Sidebar Styling */
#SidebarFrame {
    background-color: #0f172a;
    border: none;
    min-width: 250px;
    max-width: 250px;
}

#SidebarTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
    font-family: "Outfit", "Segoe UI", Arial;
    padding: 15px 10px;
    border-bottom: 1px solid #1e293b;
}

#SidebarSubtitle {
    color: #94a3b8;
    font-size: 11px;
    font-weight: normal;
    padding-bottom: 20px;
}

QPushButton.SidebarButton {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    border-radius: 6px;
    text-align: left;
    padding: 12px 18px;
    font-size: 14px;
    font-weight: 500;
    margin: 4px 10px;
}

QPushButton.SidebarButton:hover {
    background-color: #1e293b;
    color: #f8fafc;
}

QPushButton.SidebarButton:checked {
    background-color: #3b82f6;
    color: #ffffff;
    font-weight: bold;
}

/* Header Dashboard */
#HeaderFrame {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    min-height: 60px;
    max-height: 60px;
}

#HeaderTitle {
    color: #1e293b;
    font-size: 18px;
    font-weight: bold;
    padding-left: 20px;
}

#HeaderUser {
    color: #64748b;
    font-size: 13px;
    padding-right: 20px;
}

/* Main Workspace */
#WorkspaceFrame {
    background-color: #f8fafc;
}

/* ScrollArea */
QScrollArea {
    border: none;
    background-color: transparent;
}

/* Cards */
QFrame.Card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 15px;
}

QFrame.StatCard {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

#StatLabel {
    color: #64748b;
    font-size: 13px;
    font-weight: 600;
}

#StatVal {
    color: #0f172a;
    font-size: 28px;
    font-weight: bold;
}

/* Form inputs & labels */
QLabel {
    color: #334155;
    font-size: 13px;
}

QLabel.FormLabel {
    font-weight: 600;
    color: #1e293b;
    margin-top: 6px;
}

QLineEdit, QComboBox, QTextEdit, QDateEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 12px;
    color: #1e293b;
    font-size: 13px;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus, QDateEdit:focus {
    border: 1.5px solid #3b82f6;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

/* Tables */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #e2e8f0;
    color: #334155;
    font-size: 13px;
}

QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid #f1f5f9;
}

QTableWidget::item:selected {
    background-color: #eff6ff;
    color: #1d4ed8;
}

QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    padding: 10px;
    border: none;
    border-bottom: 2px solid #e2e8f0;
    font-weight: bold;
    font-size: 12px;
}

/* Buttons */
QPushButton.PrimaryButton {
    background-color: #3b82f6;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton.PrimaryButton:hover {
    background-color: #2563eb;
}

QPushButton.PrimaryButton:pressed {
    background-color: #1d4ed8;
}

QPushButton.SuccessButton {
    background-color: #10b981;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton.SuccessButton:hover {
    background-color: #059669;
}

QPushButton.DangerButton {
    background-color: #ef4444;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton.DangerButton:hover {
    background-color: #dc2626;
}

QPushButton.SecondaryButton {
    background-color: #e2e8f0;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton.SecondaryButton:hover {
    background-color: #cbd5e1;
}

/* Dialog Box */
QDialog {
    background-color: #f8fafc;
}

/* Scrollbar Customization */
QScrollBar:vertical {
    border: none;
    background-color: #f1f5f9;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}
"""

def apply_shadow(widget, color=QColor(0, 0, 0, 30), radius=10, dx=0, dy=4):
    """Apply a graphics drop shadow effect to a widget."""
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(radius)
    effect.setColor(color)
    effect.setOffset(dx, dy)
    widget.setGraphicsEffect(effect)
