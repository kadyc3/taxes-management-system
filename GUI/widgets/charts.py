import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt6.QtCore import Qt, QRectF
from typing import Dict, List, Tuple

class DonutChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data: Dict[str, float] = {}
        self.colors: Dict[str, QColor] = {}
        self.setMinimumSize(180, 180)

    def set_data(self, data: Dict[str, float], colors: Dict[str, QColor]):
        self.data = data
        self.colors = colors
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        size = min(width, height) - 20
        if size <= 0:
            return

        rect = QRectF((width - size) / 2, (height - size) / 2, size, size)
        total = sum(self.data.values())

        if total == 0:
            # Draw gray empty chart
            painter.setBrush(QBrush(QColor("#334155")))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPie(rect, 0, 360 * 16)

            # Center Hole
            hole_size = size * 0.65
            hole_rect = QRectF((width - hole_size) / 2, (height - hole_size) / 2, hole_size, hole_size)
            painter.setBrush(QBrush(QColor("#1e293b")))  # Matches slate CardFrame bg
            painter.drawEllipse(hole_rect)

            painter.setPen(QColor("#94a3b8"))
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No Data")
            return

        start_angle = 90 * 16  # Start drawing at 12 o'clock
        for label, val in self.data.items():
            if val == 0:
                continue
            span_angle = int((val / total) * 360 * 16)
            color = self.colors.get(label, QColor("#64748b"))
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPie(rect, start_angle, span_angle)
            start_angle += span_angle

        # Donut Cutout
        hole_size = size * 0.70
        hole_rect = QRectF((width - hole_size) / 2, (height - hole_size) / 2, hole_size, hole_size)
        painter.setBrush(QBrush(QColor("#1e293b")))
        painter.drawEllipse(hole_rect)

        # Center Label Text
        painter.setPen(QColor("#f8fafc"))
        font_total = QFont("Segoe UI", 16, QFont.Weight.Bold)
        painter.setFont(font_total)
        painter.drawText(
            QRectF((width - size) / 2, (height - 35) / 2, size, 25),
            Qt.AlignmentFlag.AlignCenter,
            f"{int(total)}"
        )

        painter.setPen(QColor("#94a3b8"))
        font_lbl = QFont("Segoe UI", 8, QFont.Weight.Medium)
        painter.setFont(font_lbl)
        painter.drawText(
            QRectF((width - size) / 2, (height + 15) / 2, size, 15),
            Qt.AlignmentFlag.AlignCenter,
            "TOTAL"
        )


class BarChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data: List[Tuple[str, float]] = []
        self.setMinimumSize(250, 180)

    def set_data(self, data: List[Tuple[str, float]]):
        self.data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        padding_left = 60
        padding_right = 20
        padding_top = 25
        padding_bottom = 30

        graph_width = width - padding_left - padding_right
        graph_height = height - padding_top - padding_bottom

        if graph_width <= 0 or graph_height <= 0:
            return

        # Draw axes
        painter.setPen(QPen(QColor("#475569"), 1))
        painter.drawLine(padding_left, padding_top + graph_height, padding_left + graph_width, padding_top + graph_height)
        painter.drawLine(padding_left, padding_top, padding_left, padding_top + graph_height)

        if not self.data:
            painter.setPen(QColor("#94a3b8"))
            painter.setFont(QFont("Segoe UI", 10))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No Revenue History")
            return

        max_val = max(val for label, val in self.data)
        if max_val == 0:
            max_val = 1.0

        num_bars = len(self.data)
        bar_gap = 20
        total_gaps_width = bar_gap * (num_bars + 1)
        bar_width = (graph_width - total_gaps_width) / num_bars

        # Draw Y Ticks & Grid Lines
        num_ticks = 4
        font_axis = QFont("Segoe UI", 8)
        painter.setFont(font_axis)

        for i in range(num_ticks + 1):
            y_val = max_val * (i / num_ticks)
            y_pos = padding_top + graph_height - (i / num_ticks) * graph_height

            # Grid Line
            if i > 0:
                painter.setPen(QPen(QColor("#334155"), 1, Qt.PenStyle.DashLine))
                painter.drawLine(padding_left, int(y_pos), padding_left + graph_width, int(y_pos))

            # Y Value label
            painter.setPen(QColor("#94a3b8"))
            if y_val >= 1000:
                lbl_text = f"${y_val / 1000:.1f}k"
            else:
                lbl_text = f"${y_val:.0f}"
            painter.drawText(
                10,
                int(y_pos - 6),
                padding_left - 15,
                12,
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                lbl_text
            )

        # Draw Bars
        bar_color = QColor("#3b82f6")  # Blue Accent

        for idx, (label, val) in enumerate(self.data):
            bar_height = (val / max_val) * graph_height
            x_pos = padding_left + bar_gap + idx * (bar_width + bar_gap)
            y_pos = padding_top + graph_height - bar_height

            # Draw Rect
            painter.setBrush(QBrush(bar_color))
            painter.setPen(Qt.PenStyle.NoPen)
            rect = QRectF(x_pos, y_pos, bar_width, bar_height)
            painter.drawRect(rect)

            # Draw Value on top of Bar
            painter.setPen(QColor("#f8fafc"))
            val_text = f"${val / 1000:.1f}k" if val >= 1000 else f"${val:.0f}"
            painter.drawText(
                QRectF(x_pos - 10, y_pos - 15, bar_width + 20, 12),
                Qt.AlignmentFlag.AlignCenter,
                val_text
            )

            # Draw X Label
            painter.setPen(QColor("#94a3b8"))
            painter.drawText(
                QRectF(x_pos - 10, padding_top + graph_height + 6, bar_width + 20, 15),
                Qt.AlignmentFlag.AlignCenter,
                str(label)
            )
