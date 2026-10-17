"""The readouts drawn on the overlay.

Every dimension the user sets is in millimetres; `px_per_mm` (calibrated with a
real ruler in the settings window) is the only place a pixel appears. Each
widget sizes itself to its largest possible state, so nothing clips when a dot
grows or a cursor reaches the corner of the outermost box.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter, QPen
from PySide6.QtWidgets import QWidget

from .config import KIND_JOYSTICK, KIND_RUDDER, KIND_THROTTLE, WidgetConfig

NEUTRAL = QColor(0, 0, 0)               # in the deadzone
NEUTRAL_EDGE = QColor(150, 150, 150)    # so a black dot reads on a dark game
LEFT = QColor(232, 25, 44)              # red: left / below centre
RIGHT = QColor(31, 209, 58)             # green: right / above centre
GRID = QColor(128, 128, 128)
GRID_OUTER = QColor(210, 210, 210)
CURSOR = QColor(255, 255, 255)
TEXT = QColor(226, 226, 226)
TEXT_DIM = QColor(150, 150, 150)
SHADOW = QColor(0, 0, 0, 200)
FILL = QColor(60, 190, 235)             # plane throttle bar
TRACK = QColor(70, 70, 70)
MISSING = QColor(190, 120, 30)

LABEL_MM = 5.0


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


class StickWidget(QWidget):
    """Base: label strip, drag handling, and the mm -> px conversion."""

    moved = Signal(str, int, int)

    def __init__(self, cfg: WidgetConfig, px_per_mm: float, parent: QWidget | None = None):
        super().__init__(parent)
        self.cfg = cfg
        self.px_per_mm = px_per_mm
        self.show_label = True
        self.show_value = False
        self.draggable = False
        self.missing = False
        self._content_w = 0.0
        self._drag_from: QPointF | None = None
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.relayout()

    # -- geometry -------------------------------------------------------

    def mm(self, v: float) -> float:
        return v * self.px_per_mm

    def content_size_mm(self) -> tuple[float, float]:
        raise NotImplementedError

    def label_strip_px(self) -> float:
        return self.mm(LABEL_MM * 1.6) if self.show_label else 0.0

    def label_width_px(self) -> float:
        """Width of the plain label, so a short widget is not cropped to it.

        Measured without any "no device" suffix: an unplugged stick should not
        resize the widget and shuffle the whole overlay.
        """
        if not self.show_label:
            return 0.0
        fm = QFontMetricsF(self._font(LABEL_MM, bold=True))
        return fm.horizontalAdvance(self.cfg.display_label()) + self.mm(2.0)

    def relayout(self) -> None:
        w_mm, h_mm = self.content_size_mm()
        self._content_w = self.mm(w_mm)
        w = int(round(max(self._content_w, self.label_width_px())))
        h = int(round(self.mm(h_mm) + self.label_strip_px()))
        self.setFixedSize(max(w, 8), max(h, 8))
        self.move(self.cfg.x, self.cfg.y)
        self.update()

    def apply(self, cfg: WidgetConfig, px_per_mm: float, show_label: bool, show_value: bool) -> None:
        self.cfg = cfg
        self.px_per_mm = px_per_mm
        self.show_label = show_label
        self.show_value = show_value
        self.relayout()

    # -- dragging -------------------------------------------------------

    def mousePressEvent(self, ev):
        if self.draggable and ev.button() == Qt.LeftButton:
            self._drag_from = ev.position()
            ev.accept()
        else:
            ev.ignore()

    def mouseMoveEvent(self, ev):
        if self._drag_from is None:
            ev.ignore()
            return
        delta = ev.position() - self._drag_from
        nx = max(0, int(self.x() + delta.x()))
        ny = max(0, int(self.y() + delta.y()))
        if self.parentWidget() is not None:
            nx = min(nx, max(0, self.parentWidget().width() - self.width()))
            ny = min(ny, max(0, self.parentWidget().height() - self.height()))
        self.move(nx, ny)
        self.cfg.x, self.cfg.y = nx, ny
        ev.accept()

    def mouseReleaseEvent(self, ev):
        if self._drag_from is not None:
            self._drag_from = None
            self.moved.emit(self.cfg.id, self.cfg.x, self.cfg.y)
            ev.accept()
        else:
            ev.ignore()

    # -- painting -------------------------------------------------------

    def _font(self, size_mm: float, bold: bool = False) -> QFont:
        f = QFont()
        f.setPixelSize(max(8, int(round(self.mm(size_mm)))))
        f.setBold(bold)
        return f

    def _text(self, p: QPainter, rect: QRectF, flags, s: str, colour: QColor) -> None:
        """Text with a dark backing, so it survives a bright sky behind it."""
        p.setPen(SHADOW)
        p.drawText(rect.translated(self.mm(0.35), self.mm(0.35)), flags, s)
        p.setPen(colour)
        p.drawText(rect, flags, s)

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)

        strip = self.label_strip_px()
        if self.show_label:
            p.setFont(self._font(LABEL_MM, bold=True))
            r = QRectF(0, 0, self.width(), strip)
            colour = MISSING if self.missing else TEXT
            text = self.cfg.display_label()
            if self.missing:
                text += "  -  no device"
            fm = QFontMetricsF(p.font())
            text = fm.elidedText(text, Qt.ElideRight, self.width())
            self._text(p, r, Qt.AlignHCenter | Qt.AlignVCenter, text, colour)

        cw = self._content_w or self.width()
        body = QRectF((self.width() - cw) / 2.0, strip, cw, self.height() - strip)
        if self.missing:
            self._paint_missing(p, body)
        else:
            self.paint_content(p, body)
        p.end()

    def _paint_missing(self, p: QPainter, r: QRectF) -> None:
        pen = QPen(MISSING, max(1.0, self.mm(0.4)), Qt.DashLine)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawRect(r.adjusted(1, 1, -1, -1))

    def paint_content(self, p: QPainter, r: QRectF) -> None:
        raise NotImplementedError


class RudderWidget(StickWidget):
    """A horizontal slider with dead centre in the middle.

    The dot travels the track with the pedals and carries the size and colour
    language too: black at centre / in the deadzone, red growing to the left,
    green growing to the right, from `dot_mm` up to `dot_max_mm` at full
    deflection. Position says where you are, size and colour say how far.
    """

    def __init__(self, *a, **kw):
        self.value = 0.0
        super().__init__(*a, **kw)

    def set_value(self, v: float) -> None:
        if v != self.value:
            self.value = v
            self.update()

    def track_len_mm(self) -> float:
        return max(self.cfg.track_mm, self.cfg.dot_max_mm)

    def content_size_mm(self) -> tuple[float, float]:
        extra = 17.0 if self.show_value else 0.0
        return (self.track_len_mm() + extra, self.cfg.dot_max_mm + 1.0)

    def paint_content(self, p: QPainter, r: QRectF) -> None:
        d_max = self.mm(self.cfg.dot_max_mm)
        length = self.mm(self.track_len_mm())
        travel = (length - d_max) / 2.0
        cx = r.left() + length / 2.0
        cy = r.center().y()

        rail = max(2.0, self.mm(1.6))
        p.setPen(Qt.NoPen)
        p.setBrush(TRACK)
        p.drawRect(QRectF(cx - travel, cy - rail / 2.0, travel * 2, rail))

        p.setPen(QPen(GRID, max(1.0, self.mm(0.35))))
        for frac in (-1.0, -0.5, 0.5, 1.0):
            x = cx + travel * frac
            h = d_max * (0.42 if abs(frac) == 0.5 else 0.6)
            p.drawLine(QPointF(x, cy - h / 2), QPointF(x, cy + h / 2))

        # Dead centre, spanning the full height of the track.
        p.setPen(QPen(GRID_OUTER, max(2.0, self.mm(0.9))))
        p.drawLine(QPointF(cx, r.top()), QPointF(cx, r.bottom()))

        mag = min(1.0, abs(self.value))
        dia = self.mm(_lerp(self.cfg.dot_mm, self.cfg.dot_max_mm, mag))
        x = cx + max(-1.0, min(1.0, self.value)) * travel
        if self.value == 0.0:
            p.setPen(QPen(CURSOR, max(2.0, self.mm(0.8))))
            p.setBrush(NEUTRAL)
        else:
            fill = LEFT if self.value < 0 else RIGHT
            p.setPen(QPen(fill.darker(160), max(1.0, self.mm(0.5))))
            p.setBrush(fill)
        p.drawEllipse(QPointF(x, cy), dia / 2.0, dia / 2.0)

        if self.show_value:
            p.setFont(self._font(4.2, bold=True))
            box = QRectF(cx + length / 2.0 + self.mm(1.5), cy - self.mm(3.5),
                         self.mm(15.5), self.mm(7))
            self._text(p, box, Qt.AlignLeft | Qt.AlignVCenter,
                       "CTR" if self.value == 0.0 else f"{self.value * 100:+.0f}%",
                       TEXT if self.value == 0.0 else TEXT_DIM)


class JoystickWidget(StickWidget):
    """Concentric squares marking equal steps of deflection, a centre dot, and
    a crosshair cursor driven by the two mapped axes.

    Box k (1..boxes) sits k * box_step_mm out from centre and marks
    k / boxes of full travel, so the outermost box is 100%.
    """

    def __init__(self, *a, **kw):
        self.x_value = 0.0
        self.y_value = 0.0
        super().__init__(*a, **kw)

    def set_values(self, x: float, y: float) -> None:
        if (x, y) != (self.x_value, self.y_value):
            self.x_value, self.y_value = x, y
            self.update()

    def reach_mm(self) -> float:
        return self.cfg.boxes * self.cfg.box_step_mm

    def content_size_mm(self) -> tuple[float, float]:
        # Room for the cursor to sit fully inside the outermost box corner.
        side = 2.0 * (self.reach_mm() + self.cfg.cursor_mm * 0.9)
        extra = 7.0 if self.show_value else 0.0
        return (side, side + extra)

    def paint_content(self, p: QPainter, r: QRectF) -> None:
        reach = self.mm(self.reach_mm())
        value_h = self.mm(7.0) if self.show_value else 0.0
        field = QRectF(r.left(), r.top(), r.width(), r.height() - value_h)
        cx, cy = field.center().x(), field.center().y()

        # Faint centre cross across the whole field, for reading deflection.
        p.setPen(QPen(QColor(90, 90, 90), max(1.0, self.mm(0.25))))
        p.drawLine(QPointF(cx - reach, cy), QPointF(cx + reach, cy))
        p.drawLine(QPointF(cx, cy - reach), QPointF(cx, cy + reach))

        n = max(1, self.cfg.boxes)
        step = self.mm(self.cfg.box_step_mm)
        for k in range(1, n + 1):
            half = step * k
            outer = k == n
            p.setPen(QPen(GRID_OUTER if outer else GRID,
                          max(1.0, self.mm(0.5 if outer else 0.3))))
            p.setBrush(Qt.NoBrush)
            p.drawRect(QRectF(cx - half, cy - half, half * 2, half * 2))

            if self.show_label:
                pct = 100.0 * k / n
                p.setFont(self._font(3.2))
                lab = QRectF(cx + half - self.mm(12), cy - half - self.mm(4.4),
                             self.mm(11.5), self.mm(4.2))
                self._text(p, lab, Qt.AlignRight | Qt.AlignBottom,
                           f"{pct:.0f}%", TEXT_DIM)

        # Centre dot.
        cd = self.mm(self.cfg.centre_dot_mm)
        if cd > 0:
            p.setPen(QPen(QColor(40, 40, 40), max(1.0, self.mm(0.3))))
            p.setBrush(QColor(235, 235, 235))
            p.drawEllipse(QPointF(cx, cy), cd / 2.0, cd / 2.0)

        # Cursor: positive roll -> right, positive pitch -> up.
        px = cx + max(-1.0, min(1.0, self.x_value)) * reach
        py = cy - max(-1.0, min(1.0, self.y_value)) * reach
        cur = self.mm(self.cfg.cursor_mm)
        arm = cur * 0.8

        p.setPen(QPen(SHADOW, max(2.0, self.mm(0.85))))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(px, py), cur / 2.0, cur / 2.0)
        p.drawLine(QPointF(px - arm, py), QPointF(px + arm, py))
        p.drawLine(QPointF(px, py - arm), QPointF(px, py + arm))

        p.setPen(QPen(CURSOR, max(1.0, self.mm(0.45))))
        p.drawEllipse(QPointF(px, py), cur / 2.0, cur / 2.0)
        p.drawLine(QPointF(px - arm, py), QPointF(px + arm, py))
        p.drawLine(QPointF(px, py - arm), QPointF(px, py + arm))

        if self.show_value:
            p.setFont(self._font(4.2, bold=True))
            box = QRectF(r.left(), field.bottom(), r.width(), value_h)
            self._text(p, box, Qt.AlignHCenter | Qt.AlignVCenter,
                       f"R {self.x_value * 100:+.0f}%   P {self.y_value * 100:+.0f}%", TEXT)


class _BarWidget(StickWidget):
    """Shared frame for the two throttles: a vertical bar and a numeral."""

    NUMERAL_MM = 11.0

    def __init__(self, *a, **kw):
        self.value = 0.0
        super().__init__(*a, **kw)

    def set_value(self, v: float) -> None:
        if v != self.value:
            self.value = v
            self.update()

    def content_size_mm(self) -> tuple[float, float]:
        return (max(self.cfg.bar_w_mm, 26.0), self.cfg.bar_h_mm + self.NUMERAL_MM)

    def bar_rect(self, r: QRectF) -> QRectF:
        w = self.mm(self.cfg.bar_w_mm)
        return QRectF(r.center().x() - w / 2.0, r.top(), w, self.mm(self.cfg.bar_h_mm))

    def paint_content(self, p: QPainter, r: QRectF) -> None:
        bar = self.bar_rect(r)
        p.setPen(Qt.NoPen)
        p.setBrush(TRACK)
        p.drawRect(bar)

        self.paint_fill(p, bar)

        p.setPen(QPen(GRID, max(1.0, self.mm(0.3))))
        for frac in self.tick_fractions():
            y = bar.bottom() - bar.height() * frac
            p.drawLine(QPointF(bar.left(), y), QPointF(bar.right(), y))

        self.paint_over(p, bar)

        p.setPen(QPen(GRID_OUTER, max(1.0, self.mm(0.5))))
        p.setBrush(Qt.NoBrush)
        p.drawRect(bar)

        p.setFont(self._font(9.0, bold=True))
        self._text(p, QRectF(r.left(), bar.bottom(), r.width(), self.mm(self.NUMERAL_MM)),
                   Qt.AlignHCenter | Qt.AlignVCenter, self.numeral(), TEXT)

    def tick_fractions(self) -> tuple[float, ...]:
        return ()

    def paint_fill(self, p: QPainter, bar: QRectF) -> None:
        raise NotImplementedError

    def paint_over(self, p: QPainter, bar: QRectF) -> None:
        pass

    def numeral(self) -> str:
        raise NotImplementedError


class ThrottlePlaneWidget(_BarWidget):
    """Idle-to-stop: fill height is the percentage, 0 at the bottom."""

    def tick_fractions(self) -> tuple[float, ...]:
        return (0.25, 0.5, 0.75)

    def paint_fill(self, p: QPainter, bar: QRectF) -> None:
        v = max(0.0, min(1.0, self.value))
        if v <= 0:
            return
        h = bar.height() * v
        p.setPen(Qt.NoPen)
        p.setBrush(FILL)
        p.drawRect(QRectF(bar.left(), bar.bottom() - h, bar.width(), h))

    def numeral(self) -> str:
        return f"{max(0.0, min(1.0, self.value)) * 100:.0f}%"


class ThrottleHeliWidget(_BarWidget):
    """Collective: the same bar, but filled from the centre detent outwards.

    Green climbing above centre, red falling below, so the direction reads at a
    glance. A heavy centre line sits on top of the fill -- centre is the thing
    this instrument exists to show, so nothing is allowed to bury it.
    """

    def tick_fractions(self) -> tuple[float, ...]:
        return (0.25, 0.75)

    def paint_fill(self, p: QPainter, bar: QRectF) -> None:
        v = max(-1.0, min(1.0, self.value))
        if v == 0.0:
            return
        mid = bar.center().y()
        h = (bar.height() / 2.0) * abs(v)
        p.setPen(Qt.NoPen)
        p.setBrush(RIGHT if v > 0 else LEFT)
        top = mid - h if v > 0 else mid
        p.drawRect(QRectF(bar.left(), top, bar.width(), h))

    def paint_over(self, p: QPainter, bar: QRectF) -> None:
        mid = bar.center().y()
        over = self.mm(1.8)
        p.setPen(QPen(GRID_OUTER, max(2.0, self.mm(0.9))))
        p.drawLine(QPointF(bar.left() - over, mid), QPointF(bar.right() + over, mid))

    def numeral(self) -> str:
        return "CTR" if self.value == 0.0 else f"{self.value * 100:+.0f}%"


def make_widget(cfg: WidgetConfig, px_per_mm: float, parent: QWidget | None = None) -> StickWidget:
    if cfg.kind == KIND_JOYSTICK:
        return JoystickWidget(cfg, px_per_mm, parent)
    if cfg.kind == KIND_THROTTLE:
        if cfg.subkind == "heli":
            return ThrottleHeliWidget(cfg, px_per_mm, parent)
        return ThrottlePlaneWidget(cfg, px_per_mm, parent)
    return RudderWidget(cfg, px_per_mm, parent)
