from __future__ import annotations
from typing import Optional, List, Tuple
import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QRect, QRectF
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QFontMetrics,
    QLinearGradient, QPainterPath,
)


class BarChartWidget(QWidget):
    """Simple bar chart drawn with QPainter."""

    def __init__(
        self,
        title: str,
        data: List[Tuple[str, float, float]],  # (label, value1, value2)
        series_labels: Tuple[str, str] = ("Total", "Validated"),
        colors: Tuple[str, str] = ("#2563eb", "#16a34a"),
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._data = data
        self._series_labels = series_labels
        self._colors = colors
        self.setMinimumHeight(240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def update_data(self, data: List[Tuple[str, float, float]]) -> None:
        self._data = data
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        if not self._data:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        pad_top = 40
        pad_bottom = 36
        pad_left = 56
        pad_right = 20

        chart_w = w - pad_left - pad_right
        chart_h = h - pad_top - pad_bottom

        # Title
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor("#1e293b"))
        painter.drawText(QRect(pad_left, 8, chart_w, 24), Qt.AlignmentFlag.AlignLeft, self._title)

        # Legend
        lx = pad_left + chart_w - 200
        for i, (lbl, col) in enumerate(zip(self._series_labels, self._colors)):
            painter.setBrush(QBrush(QColor(col)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(lx + i * 100, 12, 10, 10), 3, 3)
            painter.setFont(QFont("Segoe UI", 9))
            painter.setPen(QColor("#64748b"))
            painter.drawText(QRect(int(lx + i * 100 + 14), 8, 80, 18), Qt.AlignmentFlag.AlignVCenter, lbl)

        all_vals = [v for row in self._data for v in (row[1], row[2])]
        max_val = max(all_vals) if all_vals else 1
        if max_val == 0:
            max_val = 1

        # Grid lines
        grid_steps = 4
        painter.setPen(QPen(QColor("#f1f5f9"), 1))
        painter.setFont(QFont("Segoe UI", 8))
        for i in range(grid_steps + 1):
            y = pad_top + chart_h - int(chart_h * i / grid_steps)
            painter.drawLine(pad_left, y, pad_left + chart_w, y)
            val = int(max_val * i / grid_steps)
            painter.setPen(QColor("#94a3b8"))
            painter.drawText(QRect(0, y - 8, pad_left - 6, 16), Qt.AlignmentFlag.AlignRight, f"{val:,}")
            painter.setPen(QPen(QColor("#f1f5f9"), 1))

        # Bars
        n = len(self._data)
        group_w = chart_w / n
        bar_w = max(6, group_w * 0.28)

        for idx, (label, v1, v2) in enumerate(self._data):
            gx = pad_left + idx * group_w + group_w / 2

            for vi, (val, col) in enumerate([(v1, self._colors[0]), (v2, self._colors[1])]):
                bh = int(chart_h * val / max_val)
                bx = gx + (vi - 0.5) * bar_w * 1.2
                by = pad_top + chart_h - bh
                gradient = QLinearGradient(bx, by, bx, by + bh)
                c = QColor(col)
                c2 = QColor(col)
                c2.setAlpha(160)
                gradient.setColorAt(0, c)
                gradient.setColorAt(1, c2)
                painter.setBrush(QBrush(gradient))
                painter.setPen(Qt.PenStyle.NoPen)
                path = QPainterPath()
                path.addRoundedRect(QRectF(bx, by, bar_w, bh), 3, 3)
                painter.drawPath(path)

            # x label
            painter.setPen(QColor("#94a3b8"))
            painter.setFont(QFont("Segoe UI", 8))
            painter.drawText(
                QRect(int(gx - group_w / 2), pad_top + chart_h + 6, int(group_w), 20),
                Qt.AlignmentFlag.AlignCenter,
                label,
            )

        painter.end()


class LineChartWidget(QWidget):
    """Smooth area line chart drawn with QPainter."""

    def __init__(
        self,
        title: str,
        data: List[Tuple[str, float]],
        color: str = "#2563eb",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._data = data
        self._color = color
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def update_data(self, data: List[Tuple[str, float]]) -> None:
        self._data = data
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        if not self._data:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        pad_top = 40
        pad_bottom = 36
        pad_left = 70
        pad_right = 20

        chart_w = w - pad_left - pad_right
        chart_h = h - pad_top - pad_bottom

        # Title
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor("#1e293b"))
        painter.drawText(QRect(pad_left, 8, chart_w, 24), Qt.AlignmentFlag.AlignLeft, self._title)

        max_val = max(v for _, v in self._data) if self._data else 1
        if max_val == 0:
            max_val = 1

        # Grid
        grid_steps = 4
        painter.setPen(QPen(QColor("#f1f5f9"), 1))
        painter.setFont(QFont("Segoe UI", 8))
        for i in range(grid_steps + 1):
            y = pad_top + chart_h - int(chart_h * i / grid_steps)
            painter.drawLine(pad_left, y, pad_left + chart_w, y)
            val = int(max_val * i / grid_steps)
            label = f"{val // 1000}k" if val >= 1000 else str(val)
            painter.setPen(QColor("#94a3b8"))
            painter.drawText(QRect(0, y - 8, pad_left - 6, 16), Qt.AlignmentFlag.AlignRight, label)
            painter.setPen(QPen(QColor("#f1f5f9"), 1))

        # Points
        n = len(self._data)
        if n < 2:
            return
        pts = []
        for idx, (_, val) in enumerate(self._data):
            x = pad_left + int(idx * chart_w / (n - 1))
            y = pad_top + chart_h - int(chart_h * val / max_val)
            pts.append((x, y))

        # Fill area
        fill_path = QPainterPath()
        fill_path.moveTo(pts[0][0], pad_top + chart_h)
        fill_path.lineTo(pts[0][0], pts[0][1])
        for i in range(1, len(pts)):
            cx = (pts[i - 1][0] + pts[i][0]) / 2
            fill_path.cubicTo(cx, pts[i - 1][1], cx, pts[i][1], pts[i][0], pts[i][1])
        fill_path.lineTo(pts[-1][0], pad_top + chart_h)
        fill_path.closeSubpath()

        gradient = QLinearGradient(0, pad_top, 0, pad_top + chart_h)
        c = QColor(self._color)
        c.setAlpha(40)
        gradient.setColorAt(0, c)
        c2 = QColor(self._color)
        c2.setAlpha(4)
        gradient.setColorAt(1, c2)
        painter.fillPath(fill_path, gradient)

        # Line
        line_path = QPainterPath()
        line_path.moveTo(pts[0][0], pts[0][1])
        for i in range(1, len(pts)):
            cx = (pts[i - 1][0] + pts[i][0]) / 2
            line_path.cubicTo(cx, pts[i - 1][1], cx, pts[i][1], pts[i][0], pts[i][1])

        painter.setPen(QPen(QColor(self._color), 2.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(line_path)

        # Dots + x labels
        painter.setFont(QFont("Segoe UI", 8))
        for idx, (lbl, _) in enumerate(self._data):
            x, y = pts[idx]
            painter.setBrush(QBrush(QColor("#ffffff")))
            painter.setPen(QPen(QColor(self._color), 2))
            painter.drawEllipse(x - 4, y - 4, 8, 8)
            painter.setPen(QColor("#94a3b8"))
            painter.drawText(QRect(x - 20, pad_top + chart_h + 6, 40, 20), Qt.AlignmentFlag.AlignCenter, lbl)

        painter.end()


class DonutChartWidget(QWidget):
    """Donut chart drawn with QPainter."""

    def __init__(
        self,
        title: str,
        data: List[Tuple[str, float, str]],  # (label, value, color)
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._data = data
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def update_data(self, data: List[Tuple[str, float, str]]) -> None:
        self._data = data
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        if not self._data:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        total = sum(v for _, v, _ in self._data)
        if total == 0:
            return

        # Title
        painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        painter.setPen(QColor("#1e293b"))
        painter.drawText(QRect(16, 8, w - 32, 24), Qt.AlignmentFlag.AlignLeft, self._title)

        # Donut
        margin = 36
        donut_size = min(h - margin - 30, (w // 2) - 30)
        cx = margin + donut_size // 2
        cy = margin + donut_size // 2 + 20
        outer_r = donut_size // 2
        inner_r = int(outer_r * 0.55)

        start = 0.0
        for label, val, color in self._data:
            span = 360 * val / total
            path = QPainterPath()
            rect_outer = QRectF(cx - outer_r, cy - outer_r, outer_r * 2, outer_r * 2)
            path.moveTo(cx, cy)
            path.arcTo(rect_outer, start, span)
            path.closeSubpath()
            # cut inner hole
            inner_path = QPainterPath()
            rect_inner = QRectF(cx - inner_r, cy - inner_r, inner_r * 2, inner_r * 2)
            inner_path.addEllipse(rect_inner)
            donut_path = path.subtracted(inner_path)
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(QPen(QColor("#ffffff"), 2))
            painter.drawPath(donut_path)
            start += span

        # Center text
        painter.setPen(QColor("#1e293b"))
        painter.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        painter.drawText(QRect(cx - 40, cy - 14, 80, 20), Qt.AlignmentFlag.AlignCenter, f"{int(total):,}")
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor("#94a3b8"))
        painter.drawText(QRect(cx - 40, cy + 4, 80, 16), Qt.AlignmentFlag.AlignCenter, "Total")

        # Legend
        lx = cx + outer_r + 20
        ly = cy - outer_r
        painter.setFont(QFont("Segoe UI", 9))
        for i, (label, val, color) in enumerate(self._data):
            y = ly + i * 28
            painter.setBrush(QBrush(QColor(color)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(lx, y + 3, 12, 12), 3, 3)
            painter.setPen(QColor("#374151"))
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
            painter.drawText(QRect(lx + 18, y, 120, 18), Qt.AlignmentFlag.AlignVCenter, label)
            painter.setFont(QFont("Segoe UI", 8))
            painter.setPen(QColor("#64748b"))
            pct = f"{val / total * 100:.1f}%  ({int(val):,})"
            painter.drawText(QRect(lx + 18, y + 14, 150, 14), Qt.AlignmentFlag.AlignVCenter, pct)

        painter.end()